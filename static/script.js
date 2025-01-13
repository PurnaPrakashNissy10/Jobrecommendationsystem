const form = document.getElementById('uploadForm');
const resultContainer = document.getElementById('resultContainer');
const recommendedJobElement = document.getElementById('recommendedJob');
const skillsExtractedElement = document.getElementById('skillsExtracted');
const experienceExtractedElement = document.getElementById('experienceExtracted');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const fileInput = document.getElementById('resumeInput');
    const formData = new FormData();
    formData.append('resume', fileInput.files[0]);

    try {
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        recommendedJobElement.textContent = data.recommended_job;
        skillsExtractedElement.textContent = data.skills.join(', ');
        experienceExtractedElement.textContent = data.experience;

        resultContainer.classList.remove('d-none');
    } catch (error) {
        console.error('Error:', error);
        // Handle error, e.g., display an error message to the user
    }
});