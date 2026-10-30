const partitionSelect = document.querySelector("#partition");
const output = document.querySelector("#output");
const status = document.querySelector("#status");
const controls = document.querySelectorAll("button, select");

for (const id of ["refresh", "delete", "publish"]) {
  document.getElementById(id).hidden = !IrisRuntimeSDK.isDesktop;
}

async function run(action) {
  status.textContent = "Loading.";
  try {
    const result = await action();
    if (result !== undefined) output.textContent = JSON.stringify(result, null, 2);
    status.textContent = "Done.";
  } catch (error) {
    status.textContent = `Error: ${error.message ?? error}`;
  }
}

async function start() {
  controls.forEach(control => { control.disabled = true; });
  status.textContent = "Loading.";
  try {
    const dashboard = await IrisRuntimeSDK.getDashboard("example_dashboard");
    const source = await dashboard.getDataSource("example_source");

    let availablePartitions = [];

    async function loadPartitions() {
      const partitions = await source.listPartitions();
      availablePartitions = partitions;
      const previous = partitionSelect.value;
      partitionSelect.replaceChildren(new Option(IrisRuntimeSDK.isDesktop ? "All cached" : "All published", ""));
      for (const { values, isCached } of partitions) {
        const value = JSON.stringify(values);
        partitionSelect.add(new Option(`${values.month}${IrisRuntimeSDK.isDesktop && isCached ? " (cached)" : ""}`, value));
      }
      if (Array.from(partitionSelect.options).some(option => option.value === previous)) {
        partitionSelect.value = previous;
      }
      return partitions;
    }

    function selectedPartitions() {
      return partitionSelect.value ? [availablePartitions.find(partition => JSON.stringify(partition.values) === partitionSelect.value)] : null;
    }

    document.querySelector("#load").onclick = () =>
      run(() => source.getData({ partitions: selectedPartitions() }));
    document.querySelector("#refresh").onclick = () => run(async () => {
      const result = await source.getData({ partitions: selectedPartitions(), force_refresh: true });
      await loadPartitions();
      return result;
    });
    document.querySelector("#delete").onclick = () => run(async () => {
      await source.cleanCache(selectedPartitions());
      await loadPartitions();
    });
    document.querySelector("#publish").onclick = () => run(() => dashboard.publish());

    const partitions = await loadPartitions();
    output.textContent = JSON.stringify(partitions, null, 2);
    status.textContent = "Done.";
    controls.forEach(control => { control.disabled = false; });
  } catch (error) {
    status.textContent = `Error: ${error.message ?? error}`;
  }
}

start();



