const countries = [ /* full list like previous answer */ ];

window.addEventListener("DOMContentLoaded", () => {
  const select = document.getElementById("country");
  countries.sort().forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    select.appendChild(opt);
  });
});
