#!/usr/bin/env python


import os
import sys
from io import StringIO
from pprint import pformat
from shutil import copy as copyfile
from shutil import rmtree

from pyomo.core.base.sets import SimpleSet, _SetProduct

SE = sys.stderr
instance = None

node_count = 0
stringify = lambda x: ', '.join(str(i) for i in x)


class Storage:
    __slots__ = ('value', 'rate')  # this saves a noticeable amount of memory

    def __str__(self):
        return pformat(self.__dict__, indent=2)

    __repr__ = __str__


class Param:
    # will be common to all Parameters, so no sense in storing it N times
    stochasticset = None

    # this saves a noticeable amount of memory, and mild decrease in time
    __slots__ = ('items', 'name', 'spoint', 'param', 'my_keys', 'model_keys', 'skeys')

    def __init__(self, **kwargs):
        # At the point someone is using this class, they probably know what
        # they're doing, so intentionally die at this point if any of these
        # items are not passed.  They're all mandatory.
        name = kwargs.pop('param')  # parameter in question to modify
        spoint = kwargs.pop('spoint')  # stochastic point at which to do it
        rates = kwargs.pop('rates')  # how much to vary the parameter
        pidx = int(kwargs.pop('stochastic_index'))

        param = getattr(instance, name)  # intentionally die if not found.

        indices = tuple()
        pindex = param.index_set()

        if isinstance(pindex, _SetProduct):
            getname = lambda x: x.name
            indices = [getname(i) for i in pindex.set_tuple]
            skeys = lambda: (' '.join(str(i) for i in k) for k in self.model_keys)

            keys = param.keys()
            f = lambda x: x[pidx] == spoint
            r = lambda x: tuple(x[0:pidx] + x[pidx + 1 :])
        # reduce keys to remove stochastic parameter

        elif isinstance(pindex, SimpleSet):
            # this is under sparse keys
            indices = (param._index.name,)
            skeys = lambda: (' '.join(str(i) for i in self.model_keys))

            keys = param.keys()
            f = lambda x: x[pidx] == spoint
            r = lambda x: tuple(x[0:pidx] + x[pidx + 1 :])

        # we filter out the spoint because it's inherently known by TreeNode,
        # which "owns" /this/ Param
        model_keys = filter(f, keys)
        my_keys = map(r, model_keys)

        items = dict()

        for actual, mine in zip(model_keys, my_keys):
            rate = 1

            for pattern, r in rates:
                keys = pattern.split(',')
                match = True
                for p, t in zip(keys, mine):  # "pattern", "test"
                    if '*' == p:
                        continue
                    if t != p:
                        match = False
                        break
                if match:
                    rate = r
                    break

            items[mine] = Storage()
            try:
                items[mine].value = param[actual]  # pulled from model
            except ValueError:
                items[mine].value = 0
            items[mine].rate = rate

        self.items = items
        self.name = name
        self.spoint = spoint
        self.param = param
        self.my_keys = my_keys  # these keys are linked -- in the same
        self.model_keys = model_keys  #   order -- for zip()-ability
        self.skeys = skeys  # for later, string keys

    def __iter__(self):
        return self.items.__iter__()

    def __getitem__(self, i):
        try:
            return self.items[i]
        except:
            # it's likely the element did not exist, which hopefully means 0?
            class _tmp:
                rate = 0
                value = 0

            return _tmp()

    def __str__(self):
        x = '; '.join(f'({self[i].value}, {self[i].rate})' for i in self)
        return f'Param({self.name}): {x}'

    __repr__ = __str__

    def as_ampl(self, comment=''):
        pindex = self.param.index_set()
        if comment:
            comment = '# Decision: %s\n\n' % str(comment)

        keys = self.skeys()
        if isinstance(keys, str):
            keys = [keys]

        # Together, these functions return the length of a printed version of a
        # number, in characters.  They are used to make columns of data line up so
        # one may have an easier time getting an overall sense of a data file.
        def get_int_padding(v):
            return len(str(int(v)))

        def get_str_padding(index):
            def anonymous_function(obj):
                val = obj[index]
                return len(str(val))

            return anonymous_function

        keys = tuple(tuple(i.split()) for i in keys)
        vals = tuple(self[i].value for i in self.my_keys)
        int_padding = max(map(get_int_padding, vals))
        str_padding = [max(map(get_str_padding(i), keys)) for i in range(len(keys[0]))]
        str_format = '  %-{}s' * len(self.model_keys[0])
        str_format = str_format.format(*str_padding)

        format = '\n%%s   %%%ds%%s' % int_padding
        # works out to something like '\n  %s   %8d%-6s'
        #                                 index { val }

        data = StringIO()
        data.write(comment + 'param  %s  :=' % self.name)
        for actual_key, this_key in sorted(zip(self.model_keys, self.my_keys)):
            v = self[this_key].value
            int_part = str(int(abs(v)))
            if int_part != str(abs(v)):
                dec_part = str(abs(v))[len(int_part) :]
            else:
                dec_part = ''

            if v < 0:
                int_part = '-%d' % int_part
            index = str_format % tuple(actual_key)
            data.write(format % (index, int_part, dec_part))
        data.write('\n\t;\n')

        # return comment + data
        return data.getvalue()


class TreeNode:
    __slots__ = ('name', 'spoint', 'prob', 'params', 'bname', 'children')

    def __init__(self, *args, **kwargs):
        # At the point someone is using this class, they probably know what
        # they're doing, so intentionally die at this point if any of these
        # items are not passed.  They're all mandatory.
        self.name = kwargs.pop('name')  # name of /this/ node
        self.spoint = kwargs.pop('spoint')  # stochastic point of node
        self.prob = kwargs.pop('prob')  # conditional probability of node
        bname = kwargs.pop('filebase')  # file name minus extension
        types = kwargs.pop('types')  # names of decisions
        rates = kwargs.pop('rates')  # rates at which to vary
        sindices = kwargs.pop('stochastic_indices')

        params = rates.keys()
        myparams = dict()
        for key, decisions in rates.items():
            paramkwargs = {
                'param': key,
                'rates': (),
                'spoint': self.spoint,
                'stochastic_index': sindices[key],
            }
            if self.prob < 1:
                paramkwargs.update({'rates': decisions[self.name]})

            myparams[key] = Param(**paramkwargs)

        self.params = myparams
        self.bname = bname
        self.children = []

    def addChild(self, node):
        self.children.append(node)

    def __repr__(self):
        x = self.name
        if isinstance(self.name, tuple):
            x = ', '.join(x)
        return f'{self.spoint}({x}): ' + ', '.join(str(i) for i in self.params.values())

    def __str__(self, indent='  ', space=''):
        x = ''.join(i.__str__(indent, space + indent) for i in self.children)

        return space + repr(self) + '\n' + x

    def write_dat_files(self):
        global node_count

        # Step 1: Write my own file, if necessary
        if self.prob < 1:
            params = self.params.values()
            data = params[0].as_ampl(self.name)
            if len(params) > 1:
                data += '\n' + '\n'.join(p.as_ampl() for p in params[1:])
        else:
            data = '# Decision: HedgingStrategy (no change from R.dat)\n'

        with open(self.bname + '.dat', 'w') as f:
            f.write(data)

        node_count += 1
        inform('\b' * (len(str(node_count - 1)) + 1) + str(node_count) + ' ')

        # Step 2: Tell my children to write their files
        for c in self.children:
            for p in self.params:
                cp = c.params[p]
                for key in self.params[p]:
                    cp[key].value = self.params[p][key].value * cp[key].rate
            c.write_dat_files()

    def get_scenario_data(self):
        nodes = [self.bname]
        nodestage = [(self.bname, 's' + str(self.spoint))]
        probability = [(self.bname, self.prob)]
        scenarios = []
        children = []

        if not self.children:
            scenarios = [self.bname[2:]]
        else:
            children = [(self.bname, [c.bname for c in self.children])]

        for child in self.children:
            s, n, ns, c, p = child.get_scenario_data()
            scenarios += s
            nodes += n
            nodestage += ns
            children += c
            probability += p

        return scenarios, nodes, nodestage, children, probability


def write_scenario_file(stochasticset, tree):
    (
        scenarios,
        nodes,
        nodestage,
        children,
        probability,
    ) = tree.get_scenario_data()

    child_fmt = 'set  children[%s]  :=\n  %s\n\t;\n'
    scenario_fmt = 'S%(i)s  Rs%(i)s'
    stages_fmt = 'set  stage_variables[s{}]  :=\n  {}\n\t;'
    stagecost_fmt = 's%s StochasticPointCost[%s]'

    leaves = '\n  '.join(scenario_fmt % {'i': i} for i in scenarios)
    nodes = '\n  '.join(nodes)
    nodestage = '\n  '.join('   '.join(ns) for ns in nodestage)
    scenarios = 'S%s' % '\n  S'.join(scenarios)
    stagecost = '\n  '.join(stagecost_fmt % (s, s) for s in stochasticset)
    stages = '\n  s'.join(str(se) for se in stochasticset)

    probability = '\n  '.join('  '.join(str(i) for i in p) for p in probability)
    children = '\n'.join(child_fmt % (c[0], '\n  '.join(c[1])) for c in children)

    # XXX: Absolute hack, that currently only works for Temoa models.  I have
    # not yet thought about how to make this generic.  Can it be done?

    stage_var_sets = list()
    for se in stochasticset:  # se = "stochastic element"
        flow_keys = [index for index in instance.v_flow_out.keys() if index[0] == se]
        processes = [(t, v) for p, s, d, i, t, v, o in flow_keys if v == se]

        stage_vars = list()
        stage_vars.extend(
            sorted({'v_flow_in[{},{},{},{},{},{},{}]'.format(*index) for index in flow_keys})
        )
        stage_vars.extend(
            sorted({'v_flow_out[{},{},{},{},{},{},{}]'.format(*index) for index in flow_keys})
        )
        stage_vars.extend(sorted({'v_capacity[{},{}]'.format(*index) for index in processes}))

        stage_var_sets.append(stages_fmt.format(se, '\n  '.join(stage_vars)))

    stage_var_sets = '\n\n'.join(stage_var_sets)

    structure = """\
set  stages  :=
  s%(stages)s
	;

set  scenarios  :=
  %(scenarios)s
	;

set  nodes  :=
  %(nodes)s
	;

%(children_sets)s

%(stage_var_sets)s

param  node_stage  :=
  %(nodestage)s
	;

param  conditional_probability  :=
  %(cond_prob)s
	;

param  scenario_leaf_node  :=
  %(leaves)s
	;

param  stage_cost_variable  :=
  %(stagecost)s
	;

param  scenario_based_data  :=  False ;
"""

    structure %= dict(
        stages=stages,
        scenarios=scenarios,
        nodes=nodes,
        children_sets=children,
        stage_var_sets=stage_var_sets,
        nodestage=nodestage,
        cond_prob=probability,
        leaves=leaves,
        stagecost=stagecost,
    )

    with open('ScenarioStructure.dat', 'w') as f:
        f.write(structure)


def _create_tree(stochasticset, spoints, **kwargs):
    name = kwargs.get('name')
    bname = kwargs.get('bname')
    prob = kwargs.get('prob')
    cprob = kwargs.get('cprob')
    decision_list = kwargs.get('decisions')

    try:
        spoint = stochasticset.pop()  # stochastic point, use of pop implies ordering
    except:
        SE.write(
            '\nError: mismatch in specified stochastic set.  Does '
            'stochastic_points match the dat file?'
        )
        raise

    treekwargs = dict(
        spoint=spoint,
        name=name,
        types=kwargs.get('types'),
        rates=kwargs.get('rates'),
        filebase=bname,
        prob=prob,
        stochastic_indices=kwargs.get('stochastic_indices'),
    )

    node = TreeNode(**treekwargs)
    global node_count
    node_count += 1
    inform('\b' * (len(str(node_count - 1)) + 1) + str(node_count) + ' ')

    if spoint not in spoints:
        kwargs.update(
            name='HedgingStrategy',
            bname='%ss0' % bname,
            prob=1,
        )
        node.addChild(_create_tree(stochasticset[:], spoints, **kwargs))
    elif stochasticset:
        decisions = enumerate(decision_list)
        bname = '%ss%%d' % bname  # the format for the basename of the file
        for enum, d in decisions:
            kwargs.update(
                name=d,
                bname=bname % enum,
                prob=cprob[d],
            )
            node.addChild(_create_tree(stochasticset[:], spoints, **kwargs))

    return node


def create_tree(stochasticset, spoints, opts):
    types = opts.types
    rates = opts.rates
    cprob = opts.conditional_probability

    stochasticset.reverse()
    spoints.sort()
    spoints.reverse()

    kwargs = dict(
        name='Root',
        bname='R',
        types=types,
        rates=rates,
        cprob=cprob,
        decisions=types,
        stochastic_indices=opts.stochastic_indices,
        prob=1,  # conditional probability, but root guaranteed to occur
    )
    return _create_tree(stochasticset, spoints, **kwargs)


def inform(x):
    global verbose
    if verbose:
        SE.write(x)
        SE.flush()


def setup_directory(dname, force):
    if os.path.exists(dname):
        if os.path.isdir(dname):
            files = os.listdir(dname)
            if files and not force:
                msg = (
                    'Not empty: {}\n\nIf you want to use this directory anyway, '
                    "set 'force = True' in the options.py file."
                )
                raise Warning(msg.format(dname))

            # would be potentially useful to put this into a thread to speed up
            # the process.  like 'mv somedir to_del; rm -rf to_del &'
            rmtree(dname)
            os.mkdir(dname)
        else:
            msg = 'Error - already exists: {}'
            raise NameError(msg.format(dname))
    else:
        os.mkdir(dname)


def test_model_parameters(M, opts):
    try:
        getattr(M, opts.stochasticset)
    except:
        msg = (
            'Whoops!  The stochastic set is not available from the model.  '
            'Did you perhaps typo the name?\n'
            '  Model name: {}\n'
            '  Stochastic name: {}'
        )
        raise ValueError(msg.format(M.name, opts.stochasticset))

    try:
        for pname in opts.rates:
            param = getattr(M, pname)
    except:
        msg = (
            'Whoops!  Parameter not available from the model.  Have you '
            'perhaps typoed the name?\n'
            '  Model name: {}\n'
            '  Parameter name: {}'
        )
        raise ValueError(msg.format(M.name, pname))


def usage():
    SE.write(
        """
synopsis: pyomo_python  {0}  <options_to_import.py>

Example: pyomo_python  {0}  options/utopia_coal_vs_nuc.py

For information about the options_to_import.py file, please see
options/README.txt
""".format(sys.argv[0])
    )

    raise SystemExit


def main():
    from os import getcwd
    from os.path import abspath, basename, dirname
    from time import clock

    if len(sys.argv) < 2:
        usage()
    module_name = sys.argv[1][:-3].replace('/', '.')  # remove the '.py'

    mbase = basename(module_name)[:-3]
    mdir = abspath(dirname(module_name))
    sys.path.insert(0, mdir)

    try:
        __import__(module_name)
        opts = sys.modules[module_name]
        sys.path.pop(0)

    except ImportError:
        msg = 'Unable to import {}.\n\nRun this script with no arguments for more information.\n'
        SE.write(msg.format(sys.argv[1]))
        raise

    try:
        opts.dirname
    except AttributeError:
        opts.dirname = module_name.split('.')[-1]

    global verbose
    verbose = opts.verbose

    cwd = getcwd()

    begin = clock()
    duration = lambda: clock() - begin

    inform('[      ] Setting up working directory (%s)' % opts.dirname)
    setup_directory(opts.dirname, opts.force)
    inform('\r[%6.2f\n' % duration())

    inform('[      ] Import model definition (%s)' % opts.modelpath)
    mp = opts.modelpath
    modelbase = basename(mp)[:-3]
    modeldir = abspath(dirname(mp))

    sys.path.insert(0, modeldir)
    _temp = __import__(modelbase, globals(), locals(), ('model',))
    M = _temp.model
    del _temp
    sys.path.pop(0)

    test_model_parameters(M, opts)

    inform('\r[%6.2f\n' % duration())

    inform('[      ] Create concrete instance (%s)' % opts.dotdatpath)
    ins = M.create(opts.dotdatpath)
    inform('\r[%6.2f\n' % duration())

    global instance
    instance = ins

    inform('[      ] Collecting stochastic points from model (%s)' % M.name)
    all_spoints = sorted(getattr(ins, opts.stochasticset).value)
    try:
        spoints = list(opts.stochastic_points)
    except AttributeError:
        spoints = all_spoints

    inform('\r[%6.2f\n' % duration())

    # used for friendlier error checking
    Param.stochasticset = opts.stochasticset

    os.chdir(opts.dirname)
    inform('[      ] Building tree:                          ')
    tree = create_tree(all_spoints[:], spoints[:], opts)  # give an intentional copy
    inform('\r[%6.2f\n' % duration())

    global node_count
    node_count = 0

    inform('[      ] Writing scenario "dot dat" files:       ')
    tree.write_dat_files()
    write_scenario_file(all_spoints, tree)
    inform('\r[%6.2f] Writing scenario "dot dat" files\n' % duration())

    os.chdir(cwd)
    inform('[      ] Copying ReferenceModel.dat as scenario tree root')
    copyfile(opts.dotdatpath, '%s/ReferenceModel.dat' % opts.dirname)
    copyfile(opts.dotdatpath, '%s/R.dat' % opts.dirname)
    inform('\r[%6.2f\n' % duration())


if '__main__' == __name__:
    try:
        main()
    except Exception as e:
        if '--debug' in sys.argv:
            raise

        msg = (
            '\n\nIf you need more verbose (potentially helpful) information '
            'about this error, you can run this program again, and add the'
            ' "--debug" command line flag.\n'
        )
        msg = '\n\n' + str(e) + msg
        SE.write(msg)
