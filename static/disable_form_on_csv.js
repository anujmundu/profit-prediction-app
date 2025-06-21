const csvInput = document.getElementById("csv_file");
const manualFields = document.querySelectorAll("input[type='number']");

csvInput.addEventListener("change", function () {
    const csvUploaded = this.files.length > 0;

    manualFields.forEach(field => {
        if (csvUploaded) {
            field.removeAttribute("required");
        } else {
            field.setAttribute("required", "required");
        }
    });
});
