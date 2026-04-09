# Temoa Data I/O Subsystem

This directory contains the core data loading engine for the Temoa model. It is responsible for reading data from a SQLite database, validating it, and preparing it for instantiation in a Pyomo model.

## Architecture: Manifest-Driven Loading

The data loading process follows a declarative, **manifest-driven architecture**. This design separates the *configuration* of what to load from the *procedural logic* of how to load it. This makes the system easier to understand, maintain, and extend.

The key files are:

- `hybrid_loader.py`: The main engine. Its `HybridLoader` class orchestrates the entire process. It iterates through the manifest, fetches data, applies validation, and calls specialized "custom loaders" for components that require complex logic.
- `component_manifest.py`: **This is the primary file for developers to modify.** It contains the `build_manifest` function, which returns a declarative list of all data components to be loaded into the model. Each entry in this list is a `LoadItem`.
- `loader_manifest.py`: Defines the `LoadItem` dataclass, which is the schema for each entry in the manifest. It tells the `HybridLoader` everything it needs to know about a component: its source table, columns, validation rules, etc.

## How to Add a New Model Component

Adding new data components to the model is now a straightforward process that primarily involves editing the `component_manifest.py` file.

### Case 1: Adding a Simple Set or Parameter

This is the most common case, for a component that maps directly to a database table.

**Goal:** Add a new parameter `MyNewParam(region, tech, value)`.

**Steps:**

1. **Define the component** in `temoa/core/model.py` (e.g., `M.MyNewParam = Param(M.regions, M.tech_production)`).
2. **Open `temoa/data_io/component_manifest.py`**.
3. **Add a `LoadItem`** to the manifest list in the appropriate logical section (e.g., under `Operational Constraints`).

    ```python
    # temoa/data_io/component_manifest.py

    # ... inside the manifest list
    LoadItem(
        component=M.MyNewParam,
        table='MyNewParamTableName',
        columns=['region', 'tech', 'value'],
        # Optional: Add validation if this component should be filtered
        # by the source-trace analysis.
        validator_name='viable_rt',
        validation_map=(0, 1), # Corresponds to 'region' and 'tech' columns
    ),
    # ...
    ```

4. **You're done.** The `HybridLoader` engine will automatically handle fetching, validating, and loading this component.

### Case 2: Adding a Component with a Simple Fallback

If a component is optional and should have a default value if its table is missing, use the `fallback_data` attribute.

**Goal:** Add an optional set `MyOptionalSet(some_value)` that defaults to `[('A',), ('B',)]`.

**Steps:**

1. **Define the component** in `temoa/core/model.py`.
2. **Add a `LoadItem`** to `component_manifest.py`.

    ```python
    # temoa/data_io/component_manifest.py

    LoadItem(
        component=M.MyOptionalSet,
        table='MyOptionalSetTable',
        columns=['some_value'],
        is_table_required=False,  # Mark the table as optional
        fallback_data=[('A',), ('B',)] # Provide default data
    ),
    ```

### Case 3: Adding a Component with Complex Logic

If a component requires logic that doesn't fit the standard pattern (e.g., aggregating from multiple tables, complex myopic queries, dynamic fallbacks), use a custom loader.

**Goal:** Add a parameter `MyComplexParam` that requires special handling.

**Steps:**

1. **Define the component** in `temoa/core/model.py`.
2. **Open `temoa/data_io/hybrid_loader.py`**.
3. **Create a new custom loader method** inside the `HybridLoader` class. The method must accept `self, data, raw_data, filtered_data` as arguments.

    ```python
    # temoa/data_io/hybrid_loader.py

    # ... inside the HybridLoader class, in the custom loaders section
    def _load_my_complex_param(self, data: dict, raw_data: Sequence[tuple], filtered_data: Sequence[tuple]):
        """Custom loader for MyComplexParam."""
        M = TemoaModel()
        # --- Add your custom logic here ---
        # For example, perform a special query or transform the data.
        final_data_to_load = [(r, t, v * 2) for r, t, v in filtered_data] # Example transformation

        # Use the standard helper to load the final data
        self._load_component_data(data, M.MyComplexParam, final_data_to_load)
    ```

4. **Open `temoa/data_io/component_manifest.py`**.
5. **Add a `LoadItem`** that points to your new custom loader.

    ```python
    # temoa/data_io/component_manifest.py

    LoadItem(
        component=M.MyComplexParam,
        table='MyComplexParamTable', # Can be a real table or a placeholder
        columns=['region', 'tech', 'value'],
        # Point to your new method
        custom_loader_name='_load_my_complex_param',
        is_table_required=False # Usually False if the loader has complex logic
    ),
    ```

This pattern keeps the main engine clean while providing unlimited flexibility to handle any data loading scenario.
