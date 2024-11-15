// Code by ChatGPT to submit the dropdowns
// Function to set the value of the dropdown selection in the hidden input fields
function setDropdownValue(field, value) {
    // Set the hidden input field based on the dropdown selection
    document.getElementById(field + '-input').value = value;

    // Submit the form when an option is clicked
    document.getElementById('selector1').submit();
}