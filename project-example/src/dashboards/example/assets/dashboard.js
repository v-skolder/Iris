const dashboard = IrisRuntimeSDK.example_dashboard;
const cube = dashboard.example_cube;
const partitionSelect = document.querySelector("#partition");
const output = document.querySelector("#output");
const status = document.querySelector("#status");

for (const id of ["refresh", "delete", "publish"]) {
  document.getElementById(id).hidden = !IrisRuntimeSDK.isDesktop;
}

async function run(action) {
  status.textContent = "Loading.";
  try {
    const result = await action();
    output.textContent = JSON.stringify(result ?? null, null, 2);
    status.textContent = "Done.";
    return result;
  } catch (error) {
    status.textContent = `Error: ${error.message ?? error}`;
  }
}

async function loadPartitions() {
  const result = await cube.list_partitions();
  partitionSelect.replaceChildren(new Option("All", ""));
  for (const [values, cached] of result.partitions) {
    const value = values.join("/");
    partitionSelect.add(new Option(`${value}${cached ? " (cached)" : ""}`, value));
  }
  output.textContent = JSON.stringify(result, null, 2);
}

function selectedPartitions() {
  const value = partitionSelect.value;
  return value ? [value.split("/")] : null;
}

document.querySelector("#load").onclick = () =>
  run(() => cube.get_data({ partitions: selectedPartitions() }));
document.querySelector("#refresh").onclick = () =>
  run(() => cube.get_data({ partitions: selectedPartitions(), force_refresh: true }));
document.querySelector("#delete").onclick = () =>
  run(() => cube.delete_data({ partitions: selectedPartitions() }));
document.querySelector("#publish").onclick = () =>
  run(() => dashboard.publish({ partitions: selectedPartitions() }));

loadPartitions().catch(error => {
  status.textContent = `Error listing partitions: ${error.message ?? error}`;
});
