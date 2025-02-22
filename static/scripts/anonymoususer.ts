document.addEventListener("DOMContentLoaded", async () => {
  const response = await fetch("/api/v0/getauts/");
  const auts = await validateJson(response);

  for (const [id, autlist] of Object.entries(auts)) {
    console.log(`id=${id} : autlist=${autlist}`);

    // need to get the checkboxes and update complete in the session based on their checkedness
    const checkbox = document.getElementById(`checkbox-aut-${id}`);
    checkbox.addEventListener("click", async () => {
      // clicking the thing will take care of checking the box for me
      const response = await fetch(`/togglecomplete/${id}/`);
      const rjson = await validateJson(response);
      console.log(rjson);
    });

    // need to make a way to delete tasks
    const deletebtn = document.getElementById(`delete-aut-${id}`);
    deletebtn.addEventListener("click", async () => {
      //console.log(auts);
      delete auts[id];
      //console.log(auts);
      const replace:boolean = Object.keys(auts).length <= 0;
      const response = await fetch(`/deleteaut/${id}/`);
      const rjson = await validateJson(response);
      console.log(rjson);
      const aut = document.getElementById(`p-aut-${id}`);
      if(!replace) aut.remove();
      else aut.replaceWith(document.createElement("br"));
    });
  }
});

function validateJson(response: Response) {
  if (response.ok) {
    return response.json();
  } else {
    return Promise.reject(response);
  }
}
