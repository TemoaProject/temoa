document.addEventListener('DOMContentLoaded', function () {
    // --- Master Datasets (Read embedded JSON safely) ---
    let data = null;
    const dataEl = document.getElementById('graph-data');
    if (dataEl && dataEl.textContent) {
        try {
            data = JSON.parse(dataEl.textContent);
        } catch (e) {
            console.error('Failed to parse graph data JSON:', e);
        }
    }

    // If data failed to load, stop immediately to prevent further errors.
    if (!data) {
        console.error('Could not find or parse GRAPH_DATA. Halting script.');
        return;
    }

    const {
        nodes_json_primary: allNodesPrimary,
        edges_json_primary: allEdgesPrimary,
        nodes_json_secondary: allNodesSecondary,
        edges_json_secondary: allEdgesSecondary,
        options_json_str: optionsRaw,
        sectors_json_str: allSectors,
        color_legend_json_str: colorLegendData,
        style_legend_json_str: styleLegendData,
        primary_view_name: primaryViewName,
        secondary_view_name: secondaryViewName,
    } = data;
    const optionsObject = (typeof optionsRaw === 'string') ? JSON.parse(optionsRaw) : optionsRaw;
    // --- State ---
    let currentView = 'primary';
    let primaryViewPositions = null;
    let secondaryViewPositions = null;

    // --- DOM Elements ---
    const configWrapper = document.getElementById('config-panel-wrapper');
    const configHeader = document.querySelector('.config-panel-header');
    const configToggleButton = document.querySelector('.config-toggle-btn');
    const advancedControlsToggle = document.getElementById('advanced-controls-toggle');
    const visConfigContainer = document.getElementById('vis-config-container');
    const searchInput = document.getElementById('search-input');
    const resetButton = document.getElementById('reset-view-btn');
    const sectorTogglesContainer = document.getElementById('sector-toggles');
    const viewToggleButton = document.getElementById('view-toggle-btn');
    const graphContainer = document.getElementById('mynetwork');

    // --- Config Panel Toggle ---
    if (optionsObject.configure && optionsObject.configure.enabled) {
        optionsObject.configure.container = visConfigContainer;
        configHeader.addEventListener('click', () => {
            const isCollapsed = configWrapper.classList.toggle('collapsed');
            configToggleButton.setAttribute('aria-expanded', !isCollapsed);
        });
        advancedControlsToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const isHidden = visConfigContainer.style.display === 'none';
            visConfigContainer.style.display = isHidden ? 'block' : 'none';
            this.textContent = isHidden ? 'Hide Advanced Physics Controls' : 'Show Advanced Physics Controls';
        });
    }

    // --- Vis.js Network Initialization ---
    const nodes = new vis.DataSet(allNodesPrimary);
    const edges = new vis.DataSet(allEdgesPrimary);
    const network = new vis.Network(graphContainer, { nodes, edges }, optionsObject);

    // --- Core Functions ---
    function applyPositions(positions) {
        if (!positions) return;
        const updates = Object.keys(positions).map(nodeId => ({
            id: nodeId, x: positions[nodeId].x, y: positions[nodeId].y,
        }));
        if (updates.length > 0) nodes.update(updates);
    }

    function switchView() {
        if (currentView === 'primary') {
            primaryViewPositions = network.getPositions();
        } else {
            secondaryViewPositions = network.getPositions();
        }
        nodes.clear(); edges.clear();

        if (currentView === 'primary') {
            nodes.add(allNodesSecondary); edges.add(allEdgesSecondary);
            currentView = 'secondary';
            viewToggleButton.textContent = `Switch to ${primaryViewName}`;
            viewToggleButton.setAttribute('aria-pressed', 'true');
            applyPositions(secondaryViewPositions);
        } else {
            nodes.add(allNodesPrimary); edges.add(allEdgesPrimary);
            currentView = 'primary';
            viewToggleButton.textContent = `Switch to ${secondaryViewName}`;
            viewToggleButton.setAttribute('aria-pressed', 'false');
            applyPositions(primaryViewPositions);
        }
        applyAllFilters();
        network.fit();
    }

    function applyAllFilters() {
        // Preserve current positions so filtering doesn't reset layout
        const currentPositions = network.getPositions();
        const checkedSectors = new Set(Array.from(sectorTogglesContainer.querySelectorAll('input:checked')).map(c => c.value));
        const searchQuery = searchInput.value;
        let regex = null;
        if (searchQuery) {
            try { regex = new RegExp(searchQuery, 'i'); } catch (e) { console.error("Invalid Regex:", e); return; }
        }
        const activeNodesData = (currentView === 'primary') ? allNodesPrimary : allNodesSecondary;
        const activeEdgesData = (currentView === 'primary') ? allEdgesPrimary : allEdgesSecondary;
        const sectorFilteredNodes = activeNodesData.filter(node => {
            let match = node.group === null || node.group === undefined || checkedSectors.has(node.group);
            if (currentView === 'primary' && node.alwaysVisible === true) {
                match = true;
            }
            return match;
        });
        let visibleNodes, visibleEdges;
        if (regex) {
            const seedNodes = sectorFilteredNodes.filter(node => regex.test(node.label || node.id));
            const seedNodeIds = new Set(seedNodes.map(n => n.id));
            const nodesToShowIds = new Set(seedNodeIds);
            activeEdgesData.forEach(edge => {
                if (seedNodeIds.has(edge.from)) nodesToShowIds.add(edge.to);
                if (seedNodeIds.has(edge.to)) nodesToShowIds.add(edge.from);
            });
            visibleNodes = activeNodesData.filter(node => nodesToShowIds.has(node.id));
            visibleEdges = activeEdgesData.filter(edge => nodesToShowIds.has(edge.from) && nodesToShowIds.has(edge.to));
        } else {
            visibleNodes = sectorFilteredNodes;
            const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
            visibleEdges = activeEdgesData.filter(edge => visibleNodeIds.has(edge.from) && visibleNodeIds.has(edge.to));
        }
        nodes.clear(); edges.clear();
        nodes.add(visibleNodes); edges.add(visibleEdges);
        applyPositions(currentPositions);
    }

    function createStyleLegend() {
        const container = document.getElementById('style-legend-container');
        if (!container || !styleLegendData || styleLegendData.length === 0) return;
        styleLegendData.forEach(itemData => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            const swatch = document.createElement('div');
            swatch.className = 'legend-color-swatch';
            if (itemData.borderColor) swatch.style.borderColor = itemData.borderColor;
            if (itemData.borderWidth) swatch.style.borderWidth = itemData.borderWidth + 'px';
            const label = document.createElement('span');
            label.className = 'legend-label';
            label.textContent = itemData.label;
            item.append(swatch, label);
            container.appendChild(item);
        });
    }

    function createSectorLegend() {
        const container = document.getElementById('legend-container');
        if (!container || !colorLegendData || Object.keys(colorLegendData).length === 0) return;
        Object.keys(colorLegendData).sort().forEach(key => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            const swatch = document.createElement('div');
            swatch.className = 'legend-color-swatch';
            swatch.style.backgroundColor = colorLegendData[key];
            const label = document.createElement('span');
            label.className = 'legend-label';
            label.textContent = key;
            item.append(swatch, label);
            container.appendChild(item);
        });
    }

    function createSectorToggles() {
        if (!allSectors || allSectors.length === 0) {
            sectorTogglesContainer.style.display = 'none';
            return;
        }
        allSectors.forEach(sector => {
            const item = document.createElement('div');
            item.className = 'sector-toggle-item';
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `toggle-${sector}`;
            checkbox.value = sector;
            checkbox.checked = true;
            checkbox.addEventListener('change', applyAllFilters);
            const swatch = document.createElement('div');
            swatch.className = 'toggle-color-swatch';
            swatch.style.backgroundColor = colorLegendData[sector] || '#ccc';
            const label = document.createElement('label');
            label.htmlFor = checkbox.id;
            label.textContent = sector;
            item.append(swatch, checkbox, label);
            item.addEventListener('click', e => {
                    if (e.target.tagName === 'INPUT') return;
                    e.preventDefault();
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                });
            sectorTogglesContainer.appendChild(item);
        });
    }

    function resetView() {
        searchInput.value = "";
        primaryViewPositions = null;
        secondaryViewPositions = null;
        if (currentView !== 'primary') {
            switchView(); // This will switch back to primary and apply null positions
        } else {
            // If already on primary, just reload the original data
            nodes.clear(); edges.clear();
            nodes.add(allNodesPrimary); edges.add(allEdgesPrimary);
            applyPositions(primaryViewPositions); // Apply null to reset
            network.fit();
        }
        sectorTogglesContainer.querySelectorAll('input[type=checkbox]').forEach(c => c.checked = true);
        applyAllFilters();
    }

    function showNeighborhood(nodeId) {
        const activeNodes = (currentView === 'primary') ? allNodesPrimary : allNodesSecondary;
        const activeEdges = (currentView === 'primary') ? allEdgesPrimary : allEdgesSecondary;
        searchInput.value = "";
        const nodesToShow = new Set([nodeId]);
        activeEdges.forEach(edge => {
            if (edge.from === nodeId) nodesToShow.add(edge.to);
            else if (edge.to === nodeId) nodesToShow.add(edge.from);
        });
        const filteredNodes = activeNodes.filter(node => nodesToShow.has(node.id));
        const filteredEdges = activeEdges.filter(edge => nodesToShow.has(edge.from) && nodesToShow.has(edge.to));
        nodes.clear(); edges.clear();
        nodes.add(filteredNodes);
        edges.add(filteredEdges);
        network.fit();
    }

    // --- Event Listeners & Initial Setup ---
    if (allNodesSecondary && allNodesSecondary.length > 0) {
        viewToggleButton.textContent = `Switch to ${secondaryViewName}`;
        viewToggleButton.addEventListener('click', switchView);
    } else {
        document.getElementById('view-toggle-panel').style.display = 'none';
    }
    resetButton.addEventListener('click', resetView);
    searchInput.addEventListener('input', applyAllFilters);
    network.on("doubleClick", params => {
        if (params.nodes.length > 0) {
            showNeighborhood(params.nodes[0]);
        }
    });

    createStyleLegend();
    createSectorLegend();
    createSectorToggles();
});
