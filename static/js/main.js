// static/js/main.js

document.addEventListener("DOMContentLoaded", function () {
  const container = document.getElementById("dynamicFieldsContainer");

  function createField(fieldName, label, type, count, isRemovable) {
    const fieldDiv = document.createElement("div");
    fieldDiv.className = "mb-4";

    let fieldHTML = `
            <div class="flex items-center">
                <input class="shadow appearance-none border rounded-3xl w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline flex-grow " 
                    id="${fieldName}${count}" type="${type}" name="${fieldName}[]" placeholder="${label} ${count}">
        `;

    if (isRemovable) {
      fieldHTML += `
                <button type="button" class="remove-field-btn py-1 px-2 rounded focus:outline-none focus:shadow-outline ml-2 rotate-on-hover-180">
                    <img src="/static/images/minus.png" alt="Remove" class="w-6 h-6 ">
                </button>`;
    }

    fieldHTML += `</div>`;

    fieldDiv.innerHTML = fieldHTML;

    if (isRemovable) {
      const removeButton = fieldDiv.querySelector(".remove-field-btn");
      removeButton.addEventListener("click", function () {
        fieldDiv.remove();
      });
    }

    return fieldDiv;
  }

  function initializeDynamicFields(groupElement) {
    const fieldName = groupElement.dataset.fieldName;
    const fieldContainer = groupElement.querySelector(".field-container");
    const addButton = groupElement.querySelector(".add-field-btn");

    let fieldCount = 1;

    // Add initial field (not removable)
    const initialField = createField(
      fieldName,
      fieldName.charAt(0).toUpperCase() + fieldName.slice(1),
      getInputType(fieldName),
      fieldCount,
      false
    );
    fieldContainer.appendChild(initialField);

    // Add event listener for the add button
    addButton.addEventListener("click", function () {
      fieldCount++;
      const newField = createField(
        fieldName,
        fieldName.charAt(0).toUpperCase() + fieldName.slice(1),
        getInputType(fieldName),
        fieldCount,
        true
      );
      fieldContainer.appendChild(newField);
    });
  }

  function getInputType(fieldName) {
    switch (fieldName) {
      case "phonenum":
        return "number";
      case "email":
        return "email";
      case "odates":
        return "date";
      default:
        return "text";
    }
  }

  // Initialize all dynamic field groups
  const dynamicFieldGroups = container.querySelectorAll(".dynamic-field-group");
  dynamicFieldGroups.forEach(initializeDynamicFields);


  // Form Submission Logic
  document.getElementById("userInfoForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const userInfo = {};
    formData.forEach((value, key) => {
        if (key.endsWith('[]')) {
            key = key.slice(0, -2);
            if (!userInfo[key]) userInfo[key] = [];
            userInfo[key].push(value);
        } else {
            userInfo[key] = value;
        }
    });
    const response = await fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(userInfo),
    });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "passwords.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

});
