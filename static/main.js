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

function setDropdownValueTwo(value) {
    let selectedGrade = value;
    document.getElementById('grade-input').value = selectedGrade;

    // Submit the form when an option is clicked
    document.getElementById('selector1').submit();
}

function toggleAddGradeInput() {
    const form = document.getElementById('addGradeForm');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function toggleAddTermInput() {
    const form = document.getElementById('addTermForm');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function deleteGrade(gradeId) {
    if (confirm('Are you sure you want to delete this grade?')) {
        // Send a delete request to the server
        fetch('/delete_grade/' + gradeId, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    location.reload();  // Reload the page after successful deletion
                } else {
                    alert('Failed to delete the grade.');
                }
            });
    }
}