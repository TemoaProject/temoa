## Technology Groups in V3

### Previously...  For those familiar with previous versions
In previous Temoa versions, technology groups were strictly linked to a region.  The grouping table was keyed by
tuples.  The names of the groups were in one table, `groups` and the members were in a `tech_groups`
table keyed by region-group tuples.  This construct makes it difficult to reuse groupings of technologies without
completely duplicating the group in alternate regions.  Additionally, the Renewable Portfolio Standards tech
groupings were not included in this construct.

### Version 3 Implementation
Version 3 of Temoa generalizes the technology grouping construct.  Technology group names are defined in one table
and the members of the group are defined in a corresponding membership table, enabling a many-to-many relationship.
These group names can now be used in any of the parameters that accepts technology groups as an index.  Additionally,
this construct is used to support RPS implementations.  A user can define a common group of technologies and reuse
that name across multiple regions, or create individual groups and assign them.  It is also possible to assign
multiple groups to a region for RPS requirements.  Each group is considered a separate requirement against a
common total.

### Transitioning Databases
The database migration tool which is provided to help migrate legacy databases will populate the new group tables.
For existing technology groups, a 1-to-1 transfer is executed and the current region is prepended to the group name
in parens.  No effort is made to find common groups, so there may be duplicate group compositions under region-
specific names, and the functionality should remain consistent.  For RPS groups that tend to be highly similar,
The migration tool attempts to find a common set of members across all current region-specific requirements and to
coalesce a `RPS_common` set and members for the 'global' region into an `RPS_global` set.  If the membership set
across regions is not 100% common, the creation of these sets will fail and will print a corresponding note to
console during the transition.  In that case the user is responsible for migrating the RPS groups.
