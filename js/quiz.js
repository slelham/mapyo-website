(function () {
  const script = document.currentScript;
  const base = script.src.replace(/js\/quiz\.js.*$/, '');

  function slugFromPath() {
    let path = window.location.pathname.replace(/\/$/, '');
    if (path.endsWith('.html')) path = path.slice(0, -5);
    if (path === '' || path === '/index') return 'index';
    return path.replace(/^\//, '');
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function renderQuiz(container, quiz) {
    const { title, questions } = quiz;
    if (!questions || questions.length === 0) return;

    let phase = 'quiz';
    const answers = new Array(questions.length).fill(null);

    const section = document.createElement('section');
    section.className = 'quiz-section fade-up';
    section.setAttribute('aria-label', 'Study quiz');

    section.innerHTML = `
      <div class="quiz-section__header">
        <h2 class="quiz-section__title">Test Your Knowledge</h2>
        <p class="quiz-section__subtitle">Quiz based on this page's content</p>
      </div>
      <div class="quiz-panel" id="quizPanel"></div>
    `;

    const panel = section.querySelector('#quizPanel');

    function renderQuestions() {
      panel.innerHTML = `
        <form class="quiz-form" id="quizForm">
          ${questions.map((q, i) => `
            <fieldset class="quiz-question" data-index="${i}">
              <legend class="quiz-question__text">
                <span class="quiz-question__num">${i + 1}</span>
                ${escapeHtml(q.question)}
              </legend>
              <div class="quiz-options">
                ${q.options.map((opt, j) => `
                  <label class="quiz-option">
                    <input type="radio" name="q${i}" value="${escapeHtml(opt)}" ${answers[i] === opt ? 'checked' : ''}>
                    <span class="quiz-option__label">${escapeHtml(opt)}</span>
                  </label>
                `).join('')}
              </div>
            </fieldset>
          `).join('')}
          <div class="quiz-actions">
            <button type="submit" class="btn btn--gold quiz-submit">Check Answers</button>
          </div>
        </form>
      `;

      const form = panel.querySelector('#quizForm');
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        let allAnswered = true;
        questions.forEach((_, i) => {
          const selected = form.querySelector(`input[name="q${i}"]:checked`);
          if (!selected) {
            allAnswered = false;
          } else {
            answers[i] = selected.value;
          }
        });

        if (!allAnswered) {
          const unanswered = panel.querySelector('.quiz-question:not(:has(input:checked))');
          if (unanswered) {
            unanswered.scrollIntoView({ behavior: 'smooth', block: 'center' });
            unanswered.classList.add('quiz-question--highlight');
            setTimeout(() => unanswered.classList.remove('quiz-question--highlight'), 2000);
          }
          return;
        }

        phase = 'results';
        renderResults();
      });

      form.querySelectorAll('input[type="radio"]').forEach((input) => {
        input.addEventListener('change', () => {
          const idx = parseInt(input.name.replace('q', ''), 10);
          answers[idx] = input.value;
        });
      });
    }

    function renderResults() {
      let correct = 0;
      const results = questions.map((q, i) => {
        const userAnswer = answers[i];
        const isCorrect = userAnswer === q.correct;
        if (isCorrect) correct++;
        return { ...q, userAnswer, isCorrect, index: i };
      });

      const pct = Math.round((correct / questions.length) * 100);
      let message = 'Keep studying — review the page and try again!';
      if (pct === 100) message = 'Perfect score! You know this lesson well.';
      else if (pct >= 75) message = 'Great job! You understood most of this study.';
      else if (pct >= 50) message = 'Good effort! Review the missed questions below.';

      panel.innerHTML = `
        <div class="quiz-results">
          <div class="quiz-results__score">
            <div class="quiz-results__circle" style="--pct: ${pct}">
              <span class="quiz-results__pct">${pct}%</span>
            </div>
            <div class="quiz-results__summary">
              <h3 class="quiz-results__heading">${correct} of ${questions.length} correct</h3>
              <p class="quiz-results__message">${message}</p>
            </div>
          </div>
          <div class="quiz-results__breakdown">
            ${results.map((r) => `
              <div class="quiz-result-item ${r.isCorrect ? 'quiz-result-item--correct' : 'quiz-result-item--wrong'}">
                <div class="quiz-result-item__header">
                  <span class="quiz-result-item__icon" aria-hidden="true">${r.isCorrect ? '✓' : '✗'}</span>
                  <p class="quiz-result-item__question">
                    <strong>Q${r.index + 1}.</strong> ${escapeHtml(r.question)}
                  </p>
                </div>
                ${r.isCorrect ? `
                  <p class="quiz-result-item__answer quiz-result-item__answer--correct">
                    Your answer: ${escapeHtml(r.userAnswer)}
                  </p>
                ` : `
                  <p class="quiz-result-item__answer quiz-result-item__answer--wrong">
                    Your answer: ${escapeHtml(r.userAnswer)}
                  </p>
                  <div class="quiz-result-item__correction">
                    <p class="quiz-result-item__correct-label">Correct answer:</p>
                    <p class="quiz-result-item__correct-answer">${escapeHtml(r.correct)}</p>
                    <p class="quiz-result-item__explanation">${escapeHtml(r.explanation)}</p>
                  </div>
                `}
              </div>
            `).join('')}
          </div>
          <div class="quiz-actions">
            <button type="button" class="btn btn--gold quiz-retry" id="quizRetry">Try Again</button>
          </div>
        </div>
      `;

      panel.querySelector('#quizRetry').addEventListener('click', () => {
        phase = 'quiz';
        answers.fill(null);
        renderQuestions();
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    }

    renderQuestions();

    const mount =
      document.querySelector('article.page-content') ||
      document.querySelector('main.page .container') ||
      document.querySelector('section.contact .container') ||
      document.querySelector('main .container');

    if (mount) {
      mount.appendChild(section);
      requestAnimationFrame(() => section.classList.add('visible'));
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const slug = slugFromPath();
    fetch(`${base}data/quizzes.json`)
      .then((res) => {
        if (!res.ok) throw new Error('Quiz data not found');
        return res.json();
      })
      .then((data) => {
        const quiz = data[slug];
        if (quiz) renderQuiz(document.body, quiz);
      })
      .catch(() => {});
  });
})();