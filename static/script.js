/**
 * Frontend JavaScript for Ask The Odyssey application.
 * Handles user interactions, API calls, and UI updates.
 */

// DOM elements
const questionInput = document.getElementById('question-input');
const submitBtn = document.getElementById('submit-btn');
const loadingDiv = document.getElementById('loading');
const answerSection = document.getElementById('answer-section');
const answerText = document.getElementById('answer-text');
const sourcesDiv = document.getElementById('sources');
const errorSection = document.getElementById('error-section');
const errorText = document.getElementById('error-text');
const exampleBtns = document.querySelectorAll('.example-btn');

/**
 * Initialize event listeners when the page loads
 */
document.addEventListener('DOMContentLoaded', () => {
    // Submit button click
    submitBtn.addEventListener('click', submitQuestion);

    // Enter key in textarea (Ctrl+Enter or Cmd+Enter to submit)
    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            submitQuestion();
        }
    });

    // Example question buttons
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.getAttribute('data-question');
            questionInput.value = question;
            questionInput.focus();
            // Optionally auto-submit
            // submitQuestion();
        });
    });
});

/**
 * Submit the question to the API
 */
async function submitQuestion() {
    const question = questionInput.value.trim();

    // Validate input
    if (!question) {
        alert('Please enter a question');
        questionInput.focus();
        return;
    }

    // Update UI state
    showLoading();
    hideAnswer();
    hideError();
    disableInput();

    try {
        // Make API request
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();

        if (data.success) {
            displayAnswer(data.answer, data.sources);
        } else {
            displayError(data.error || 'An error occurred while processing your question.');
        }
    } catch (error) {
        console.error('Request failed:', error);
        displayError('Failed to connect to the server. Please check your connection and try again.');
    } finally {
        hideLoading();
        enableInput();
    }
}

/**
 * Display the answer and sources
 */
function displayAnswer(answer, sources) {
    // Set answer text
    answerText.textContent = answer;

    // Clear previous sources
    sourcesDiv.innerHTML = '';

    // Render each source
    sources.forEach((source, index) => {
        const sourceCard = createSourceCard(source, index);
        sourcesDiv.appendChild(sourceCard);
    });

    // Show answer section
    showAnswer();

    // Scroll to answer
    answerSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Create a source card element
 */
function createSourceCard(source, index) {
    const card = document.createElement('div');
    card.className = 'source-card';

    // Calculate relevance percentage
    const relevancePercent = Math.round(source.relevance_score * 100);

    card.innerHTML = `
        <div class="source-header">
            <span class="source-book">${escapeHtml(source.book)}</span>
            <div class="source-relevance">
                <span>${relevancePercent}%</span>
                <div class="relevance-bar">
                    <div class="relevance-fill" style="width: ${relevancePercent}%"></div>
                </div>
            </div>
        </div>
        <div class="source-text">${escapeHtml(source.text)}</div>
    `;

    return card;
}

/**
 * Display an error message
 */
function displayError(message) {
    errorText.textContent = message;
    showError();

    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * UI state management functions
 */

function showLoading() {
    loadingDiv.classList.remove('hidden');
}

function hideLoading() {
    loadingDiv.classList.add('hidden');
}

function showAnswer() {
    answerSection.classList.remove('hidden');
}

function hideAnswer() {
    answerSection.classList.add('hidden');
}

function showError() {
    errorSection.classList.remove('hidden');
}

function hideError() {
    errorSection.classList.add('hidden');
}

function disableInput() {
    questionInput.disabled = true;
    submitBtn.disabled = true;
}

function enableInput() {
    questionInput.disabled = false;
    submitBtn.disabled = false;
    questionInput.focus();
}
