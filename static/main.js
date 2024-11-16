// Code by ChatGPT to submit the dropdowns
// Function to set the value of the dropdown selection in the hidden input fields
function setDropdownValue(field, value) {
    // Store the selected values for grade and term
    let selectedGrade = '';
    let selectedTerm = '';

    if (field == 'grade') {
        selectedGrade = value;
        document.getElementById('grade-input').value = selectedGrade;
        document.getElementById('term-input').value = selectedTerm;
    } else if (field == 'term') {
        selectedTerm = value;
        document.getElementById('term-input').value = selectedTerm;
    }

    // Submit the form when an option is clicked
    document.getElementById('selector1').submit();
}