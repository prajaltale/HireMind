/**
 * HireMind - Frontend: Auth, dashboard, resume upload, ATS, feedback, voice interview
 */
const API_BASE = ""; // same origin when served by FastAPI

let auth = {
  token: null,
  user: null,
};

let state = {
  resumeText: "",
  jobDescription: "",
  atsData: null,
  questions: [],
  currentQuestionIndex: 0,
  evaluationResults: [],
  sessions: 0,
  avgInterviewScore: null,
};

// ---------- Auth helpers ----------
const authView = document.getElementById("authView");
const dashboardView = document.getElementById("dashboardView");
const resumeView = document.getElementById("resumeView");
const interviewView = document.getElementById("interviewView");
const profileView = document.getElementById("profileView");
const navItems = document.querySelectorAll(".nav-item[data-view]");

const statLastScore = document.getElementById("statLastScore");
const statSessions = document.getElementById("statSessions");
const statAvgInterview = document.getElementById("statAvgInterview");

const userNameEl = document.getElementById("userName");
const userEmailEl = document.getElementById("userEmail");
const userAvatarEl = document.getElementById("userAvatar");
const profileEmail = document.getElementById("profileEmail");
const profileName = document.getElementById("profileName");

const btnLogout = document.getElementById("btnLogout");

const authTabs = document.querySelectorAll(".auth-tab");
const authForm = document.getElementById("authForm");
const fieldName = document.getElementById("fieldName");
const authName = document.getElementById("authName");
const authEmail = document.getElementById("authEmail");
const authPassword = document.getElementById("authPassword");
const btnAuthSubmit = document.getElementById("btnAuthSubmit");
const btnGoogleSignIn = document.getElementById("btnGoogleSignIn");

let authMode = "login"; // or "register"

function loadAuthFromStorage() {
  const token = window.localStorage.getItem("hm_token");
  const userStr = window.localStorage.getItem("hm_user");
  if (token && userStr) {
    try {
      auth.token = token;
      auth.user = JSON.parse(userStr);
    } catch {
      auth.token = null;
      auth.user = null;
    }
  }
}

function persistAuth() {
  if (auth.token && auth.user) {
    window.localStorage.setItem("hm_token", auth.token);
    window.localStorage.setItem("hm_user", JSON.stringify(auth.user));
  } else {
    window.localStorage.removeItem("hm_token");
    window.localStorage.removeItem("hm_user");
  }
}

function setAuth(token, user) {
  auth.token = token;
  auth.user = user;
  persistAuth();
  syncAuthUI();
}

function logout() {
  auth.token = null;
  auth.user = null;
  persistAuth();
  syncAuthUI();
}

function syncAuthUI() {
  const isAuthed = !!auth.token && !!auth.user;
  if (isAuthed) {
    authView.classList.add("hidden");
    dashboardView.classList.remove("hidden");
    navItems.forEach((btn) => btn.removeAttribute("disabled"));
    btnLogout.disabled = false;
    const email = auth.user.email || "";
    const name = auth.user.name || email || "User";
    userNameEl.textContent = name;
    userEmailEl.textContent = email || "Signed in";
    userAvatarEl.textContent = (name || email || "?").charAt(0).toUpperCase();
    profileEmail.textContent = email || "–";
    profileName.textContent = name || "–";
    // Load dashboard stats when authenticated
    loadDashboardStats();
  } else {
    authView.classList.remove("hidden");
    dashboardView.classList.add("hidden");
    resumeView.classList.add("hidden");
    interviewView.classList.add("hidden");
    profileView.classList.add("hidden");
    navItems.forEach((btn) => btn.setAttribute("disabled", "disabled"));
    btnLogout.disabled = true;
    userNameEl.textContent = "Guest";
    userEmailEl.textContent = "Not signed in";
    userAvatarEl.textContent = "?";
    profileEmail.textContent = "–";
    profileName.textContent = "–";
  }
}

function switchView(viewId) {
  if (!auth.token) {
    alert("Please sign in first.");
    return;
  }
  [dashboardView, resumeView, interviewView, profileView].forEach((el) =>
    el.classList.add("hidden")
  );
  const target = document.getElementById(viewId);
  if (target) target.classList.remove("hidden");
}

navItems.forEach((btn) => {
  btn.addEventListener("click", () => {
    if (btn.hasAttribute("disabled")) return;
    navItems.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const view = btn.getAttribute("data-view");
    if (view) switchView(view);
  });
});

btnLogout.addEventListener("click", () => {
  logout();
});

authTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    authTabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    authMode = tab.getAttribute("data-mode") || "login";
    if (authMode === "register") {
      fieldName.classList.remove("hidden");
      btnAuthSubmit.textContent = "Create account";
    } else {
      fieldName.classList.add("hidden");
      btnAuthSubmit.textContent = "Sign in";
    }
  });
});

authForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = authEmail.value.trim();
  const password = authPassword.value;
  const name = authName.value.trim();
  if (!email || !password || (authMode === "register" && !name)) {
    alert("Please fill all required fields.");
    return;
  }
  btnAuthSubmit.disabled = true;
  try {
    const path = authMode === "register" ? "/api/auth/register" : "/api/auth/login";
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(
        authMode === "register" ? { email, password, name } : { email, password }
      ),
    });
    if (!res.ok) {
      let msg = "Auth failed";
      try {
        const body = await res.json();
        if (body && body.detail) msg = body.detail;
      } catch {
        msg = `HTTP ${res.status}`;
      }
      throw new Error(msg);
    }
    const data = await res.json();
    setAuth(data.access_token, data.user);
    switchView("dashboardView");
  } catch (err) {
    alert("Auth error: " + err.message);
  }
  btnAuthSubmit.disabled = false;
});

btnGoogleSignIn.addEventListener("click", async () => {
  const email = window.prompt(
    "Demo Google sign-in: enter your Google email (no real verification is performed)."
  );
  if (!email) return;
  const name = email.split("@")[0];
  try {
    const res = await fetch(`${API_BASE}/api/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, name }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Google sign-in failed");
    const data = await res.json();
    setAuth(data.access_token, data.user);
    switchView("dashboardView");
  } catch (err) {
    alert("Google sign-in error: " + err.message);
  }
});

function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (auth.token) {
    headers["Authorization"] = `Bearer ${auth.token}`;
  }
  return fetch(`${API_BASE}${path}`, { ...options, headers });
}

// ---------- Dashboard Stats Loading ----------
async function loadDashboardStats() {
  if (!auth.token) {
    console.log("No auth token, skipping dashboard stats load");
    return;
  }
  try {
    const r = await apiFetch("/api/dashboard/stats");
    if (!r.ok) {
      console.error("Failed to fetch dashboard stats, status:", r.status);
      const errorData = await r.json();
      console.error("Error details:", errorData);
      return;
    }
    const data = await r.json();
    console.log("Dashboard stats loaded:", data);
    // Handle values properly - don't use || because 0 is falsy
    statLastScore.textContent = data.last_ats_score !== null && data.last_ats_score !== undefined ? data.last_ats_score : "–";
    statSessions.textContent = data.sessions_count !== null && data.sessions_count !== undefined ? String(data.sessions_count) : "0";
    statAvgInterview.textContent = data.avg_interview_score !== null && data.avg_interview_score !== undefined ? data.avg_interview_score : "–";
    console.log("Dashboard updated successfully", {
      lastScore: statLastScore.textContent,
      sessions: statSessions.textContent,
      avgInterview: statAvgInterview.textContent
    });
  } catch (e) {
    console.error("Error loading dashboard stats:", e);
  }
}

// ---------- Resume Upload ----------
const uploadZone = document.getElementById("uploadZone");
const resumeFile = document.getElementById("resumeFile");
const uploadLabel = document.getElementById("uploadLabel");
const parseStatus = document.getElementById("parseStatus");

uploadZone.addEventListener("click", () => resumeFile.click());
uploadZone.addEventListener("dragover", (e) => { e.preventDefault(); uploadZone.classList.add("dragover"); });
uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("dragover"));
uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.classList.remove("dragover");
  const file = e.dataTransfer?.files?.[0];
  if (file && file.name.toLowerCase().endsWith(".pdf")) parseAndUpload(file);
});

resumeFile.addEventListener("change", () => {
  const file = resumeFile.files?.[0];
  if (file) parseAndUpload(file);
});

async function parseAndUpload(file) {
  parseStatus.textContent = "Parsing...";
  parseStatus.classList.remove("hidden");
  const form = new FormData();
  form.append("file", file);
  try {
    const r = await apiFetch("/api/parse-resume", { method: "POST", body: form });
    if (!r.ok) throw new Error((await r.json()).detail || "Parse failed");
    const data = await r.json();
    state.resumeText = data.text || "";
    parseStatus.textContent = state.resumeText ? `Resume parsed (${state.resumeText.length} chars).` : "No text extracted.";
  } catch (e) {
    parseStatus.textContent = "Error: " + e.message;
  }
}

// ---------- Job Description (sync to state) ----------
const jobDescEl = document.getElementById("jobDesc");
jobDescEl.addEventListener("input", () => { state.jobDescription = jobDescEl.value.trim(); });

// ---------- ATS Score ----------
const btnAts = document.getElementById("btnAts");
const atsResult = document.getElementById("atsResult");
const atsCircle = document.getElementById("atsCircle");
const atsScoreNum = document.getElementById("atsScoreNum");
const matchedSkills = document.getElementById("matchedSkills");
const missingSkills = document.getElementById("missingSkills");

btnAts.addEventListener("click", async () => {
  if (!state.resumeText || !state.jobDescription) {
    alert("Please upload a resume and enter a job description.");
    return;
  }
  btnAts.disabled = true;
  btnAts.textContent = "Calculating...";
  try {
    const r = await apiFetch("/api/ats-score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: state.resumeText, job_description: state.jobDescription }),
    });
    if (!r.ok) throw new Error((await r.json()).detail || "ATS failed");
    const data = await r.json();
    state.atsData = data;
    atsScoreNum.textContent = data.score;
    const deg = (data.score / 100) * 360;
    atsCircle.style.background = `conic-gradient(var(--accent) ${deg}deg, var(--border) 0deg)`;
    matchedSkills.innerHTML = (data.matched_skills || []).slice(0, 30).map(s => `<span class="skill-tag matched">${escapeHtml(s)}</span>`).join("");
    missingSkills.innerHTML = (data.missing_skills || []).slice(0, 30).map(s => `<span class="skill-tag missing">${escapeHtml(s)}</span>`).join("");
    atsResult.classList.remove("hidden");
    // Reload dashboard after ATS score is calculated
    await loadDashboardStats();
  } catch (e) {
    alert("ATS error: " + e.message);
  }
  btnAts.disabled = false;
  btnAts.textContent = "Calculate ATS Score";
});

// ---------- AI Resume Feedback ----------
const btnFeedback = document.getElementById("btnFeedback");
const feedbackResult = document.getElementById("feedbackResult");
const feedbackStrengths = document.getElementById("feedbackStrengths");
const feedbackWeaknesses = document.getElementById("feedbackWeaknesses");
const feedbackSuggestions = document.getElementById("feedbackSuggestions");
const feedbackRecommendation = document.getElementById("feedbackRecommendation");

btnFeedback.addEventListener("click", async () => {
  if (!state.resumeText || !state.jobDescription) {
    alert("Please upload a resume and enter a job description.");
    return;
  }
  btnFeedback.disabled = true;
  btnFeedback.textContent = "Generating...";
  try {
    const r = await apiFetch("/api/resume-feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: state.resumeText, job_description: state.jobDescription }),
    });
    if (!r.ok) throw new Error((await r.json()).detail || "Feedback failed");
    const data = await r.json();
    feedbackStrengths.innerHTML = (data.strengths || []).map(s => `<li>${escapeHtml(s)}</li>`).join("");
    feedbackWeaknesses.innerHTML = (data.weaknesses || []).map(w => `<li>${escapeHtml(w)}</li>`).join("");
    feedbackSuggestions.innerHTML = (data.suggestions || []).map(s => `<li>${escapeHtml(s)}</li>`).join("");
    feedbackRecommendation.textContent = data.recommendation || "";
    feedbackResult.classList.remove("hidden");
  } catch (e) {
    alert("Feedback error: " + e.message);
  }
  btnFeedback.disabled = false;
  btnFeedback.textContent = "Get AI Feedback";
});

// ---------- Voice Interview ----------
const btnStartInterview = document.getElementById("btnStartInterview");
const interviewArea = document.getElementById("interviewArea");
const currentQNum = document.getElementById("currentQNum");
const totalQNum = document.getElementById("totalQNum");
const currentQuestion = document.getElementById("currentQuestion");
const answerText = document.getElementById("answerText");
const btnSpeakQuestion = document.getElementById("btnSpeakQuestion");
const btnRecord = document.getElementById("btnRecord");
const recordStatus = document.getElementById("recordStatus");
const btnEvaluate = document.getElementById("btnEvaluate");
const btnNextQuestion = document.getElementById("btnNextQuestion");
const btnEndInterview = document.getElementById("btnEndInterview");
const evalResult = document.getElementById("evalResult");

let recognition = null;
let synth = window.speechSynthesis;

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return null;
  const r = new SpeechRecognition();
  r.continuous = true;
  r.interimResults = true;
  r.lang = "en-US";
  r.onresult = (e) => {
    const last = e.results.length - 1;
    const transcript = Array.from(e.results[last]).map(r => r.transcript).join("");
    if (e.results[last].isFinal) {
      const current = answerText.textContent.trim();
      answerText.textContent = (current ? current + " " : "") + transcript;
      answerText.classList.add("has-content");
    }
  };
  r.onend = () => { recordStatus.textContent = "Stopped"; recordStatus.classList.remove("recording"); };
  return r;
}

recognition = initSpeechRecognition();

btnStartInterview.addEventListener("click", async () => {
  if (!state.resumeText || !state.jobDescription) {
    alert("Please upload a resume and enter a job description first.");
    return;
  }
  btnStartInterview.disabled = true;
  btnStartInterview.textContent = "Generating...";
  try {
    const r = await apiFetch("/api/interview/questions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: state.resumeText,
        job_description: state.jobDescription,
        count: 5,
      }),
    });
    if (!r.ok) throw new Error((await r.json()).detail || "Failed to get questions");
    const data = await r.json();
    state.questions = data.questions || [];
    state.currentQuestionIndex = 0;
    state.evaluationResults = [];
    totalQNum.textContent = state.questions.length;
    showCurrentQuestion();
    interviewArea.classList.remove("hidden");
  } catch (e) {
    alert("Error: " + e.message);
  }
  btnStartInterview.disabled = false;
  btnStartInterview.textContent = "Generate Questions & Start";
});

function showCurrentQuestion() {
  if (state.questions.length === 0) return;
  const q = state.questions[state.currentQuestionIndex];
  currentQNum.textContent = state.currentQuestionIndex + 1;
  currentQuestion.textContent = q || "(No question)";
  answerText.textContent = "";
  answerText.classList.remove("has-content");
  evalResult.classList.add("hidden");
  evalResult.innerHTML = "";
}

function speakQuestion() {
  const q = currentQuestion.textContent;
  if (!q || !synth) return;
  synth.cancel();
  const u = new SpeechSynthesisUtterance(q);
  u.rate = 0.95;
  u.pitch = 1;
  synth.speak(u);
}

btnSpeakQuestion.addEventListener("click", speakQuestion);

btnRecord.addEventListener("click", () => {
  if (!recognition) {
    alert("Speech recognition not supported in this browser.");
    return;
  }
  if (recordStatus.classList.contains("recording")) {
    recognition.stop();
    return;
  }
  recordStatus.textContent = "Listening...";
  recordStatus.classList.add("recording");
  recognition.start();
});

btnEvaluate.addEventListener("click", async () => {
  const question = currentQuestion.textContent;
  const answer = answerText.textContent.trim();
  if (!question || !answer) {
    alert("Please record or type an answer first.");
    return;
  }
  btnEvaluate.disabled = true;
  evalResult.classList.remove("hidden");
  evalResult.innerHTML = '<div class="spinner"></div> Evaluating...';
  try {
    const r = await apiFetch("/api/interview/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        answer_text: answer,
        resume_text: state.resumeText,
        job_description: state.jobDescription,
      }),
    });
    if (!r.ok) throw new Error((await r.json()).detail || "Evaluation failed");
    const data = await r.json();
    state.evaluationResults[state.currentQuestionIndex] = data;
    let html = `<div class="score">Score: ${data.score}/10</div>`;
    if (data.strengths?.length) html += `<p><strong>Strengths:</strong> ${data.strengths.join("; ")}</p>`;
    if (data.weaknesses?.length) html += `<p><strong>Weaknesses:</strong> ${data.weaknesses.join("; ")}</p>`;
    if (data.suggestions?.length) html += `<p><strong>Suggestions:</strong> ${data.suggestions.join("; ")}</p>`;
    evalResult.innerHTML = html;
    // Optional: speak feedback (short)
    if (synth && data.score !== undefined) {
      synth.cancel();
      const u = new SpeechSynthesisUtterance(`Score ${data.score} out of 10. ${(data.suggestions && data.suggestions[0]) ? data.suggestions[0] : ""}`);
      u.rate = 0.9;
      synth.speak(u);
    }
  } catch (e) {
    evalResult.innerHTML = "Error: " + escapeHtml(e.message);
  }
  btnEvaluate.disabled = false;
});

btnNextQuestion.addEventListener("click", () => {
  if (state.currentQuestionIndex < state.questions.length - 1) {
    state.currentQuestionIndex++;
    showCurrentQuestion();
  } else {
    alert("You have answered all questions. Click 'End Interview' to finish and see your results on the dashboard.");
  }
});

btnEndInterview.addEventListener("click", async () => {
  const total = state.evaluationResults.filter(Boolean).length;
  const avg = total ? state.evaluationResults.reduce((s, e) => s + (e.score || 0), 0) / total : 0;
  
  console.log("Interview ended with:", {
    total_questions: state.questions.length,
    answered: total,
    average_score: avg,
    results: state.evaluationResults
  });
  
  // Show saving message
  alert("Saving your interview results...");
  
  // Save session to backend
  try {
    const response = await apiFetch("/api/interview/save-session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question_count: state.questions.length,
        average_score: avg,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error("Failed to save session:", response.status, errorData);
      alert("Error: Could not save session to database. " + errorData.detail);
    } else {
      console.log("Session saved successfully");
      alert(`Interview complete! You answered ${total} questions. Average score: ${avg.toFixed(1)}/10.`);
    }
  } catch (e) {
    console.error("Error saving session:", e);
    alert("Error: Could not save session: " + e.message);
  }
  
  // Wait a moment then update dashboard stats
  await new Promise(resolve => setTimeout(resolve, 500));
  console.log("Loading dashboard stats...");
  await loadDashboardStats();
  
  // Hide interview area and switch back to dashboard view to show updated stats
  interviewArea.classList.add("hidden");
  switchView("dashboardView");
});

// Placeholder for contenteditable
answerText.addEventListener("focus", function () {
  if (this.textContent.trim() === "" && this.getAttribute("data-placeholder")) {
    this.classList.remove("has-content");
  }
});
answerText.addEventListener("input", function () {
  if (this.textContent.trim()) this.classList.add("has-content");
});
answerText.addEventListener("blur", function () {
  if (this.textContent.trim() === "") this.classList.remove("has-content");
});

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

// ---------- Initial boot ----------
loadAuthFromStorage();
syncAuthUI();
switchView("dashboardView");
