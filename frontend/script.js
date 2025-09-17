let pyodide = null;
let computeGpaPyFn = null;

const state = {
  semesterId: null,
  courses: [], // fetched from backend
  gradeInputs: new Map() // courseId -> input element
};

async function initPy() {
  pyodide = await loadPyodide();
  const pyCode = `
def compute_gpa(grade_points, credit_hours):
    ch = sum(int(x) for x in credit_hours)
    total_gp = 0.0
    for g, c in zip(grade_points, credit_hours):
        total_gp += float(g) * int(c)
    gpa = round(total_gp / ch, 2) if ch else 0.0
    return {"gpa": gpa, "total_gp": round(total_gp, 2), "total_ch": ch}
`;
  pyodide.runPython(pyCode);
  computeGpaPyFn = pyodide.globals.get("compute_gpa");
}

function qs(sel){ return document.querySelector(sel); }
function qsa(sel){ return Array.from(document.querySelectorAll(sel)); }

function show(sectionId){
  qs("#home").classList.add("hidden");
  qs("#semester-ui").classList.add("hidden");
  qs(sectionId).classList.remove("hidden");
}

async function fetchCourses(semesterId){
  const url = `${window.API_BASE_URL}/api/semesters/${semesterId}/courses`;
  const res = await fetch(url);
  if(!res.ok){ throw new Error("Failed to fetch courses"); }
  return await res.json();
}

function buildTable(courses){
  const tbody = qs("#courses-body");
  tbody.innerHTML = "";
  state.gradeInputs.clear();

  for(const c of courses){
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${c.sr_no}</td>
      <td>${c.course_code}</td>
      <td>${c.course_name}</td>
      <td>${c.credit_hours}</td>
      <td><input type="number" min="0" max="4" step="0.01" placeholder="e.g., 3.30" data-course="${c.id}"/></td>
      <td class="row-total" data-course="${c.id}">0.00</td>
    `;
    tbody.appendChild(tr);
    const input = tr.querySelector("input");
    input.addEventListener("input", onGradeChange);
    state.gradeInputs.set(c.id, input);
  }
  updateSummary();
}

function onGradeChange(e){
  const input = e.target;
  const courseId = parseInt(input.dataset.course, 10);
  const course = state.courses.find(c => c.id === courseId);
  const val = parseFloat(input.value);
  const cell = qs(`.row-total[data-course="${courseId}"]`);
  let rowTotal = 0.0;
  if(!isNaN(val) && val >= 0 && val <= 4 && course){
    rowTotal = val * course.credit_hours;
  }
  cell.textContent = rowTotal.toFixed(2);
  updateSummary();
}

function allFilled(){
  for(const [, input] of state.gradeInputs){
    const v = parseFloat(input.value);
    if(isNaN(v) || v < 0 || v > 4){
      return false;
    }
  }
  return true;
}

function collectArrays(){
  const gradePoints = [];
  const creditHours = [];
  for(const c of state.courses){
    const inp = state.gradeInputs.get(c.id);
    gradePoints.push(parseFloat(inp.value));
    creditHours.push(c.credit_hours);
  }
  return {gradePoints, creditHours};
}

function updateSummary(){
  const {gradePoints, creditHours} = collectArrays();
  let totalGp = 0.0;
  let totalCh = 0;
  for(let i=0;i<gradePoints.length;i++){
    const g = gradePoints[i];
    const ch = creditHours[i];
    if(!isNaN(g)){
      totalGp += g * ch;
    }
    totalCh += ch;
  }
  qs("#total-gp").textContent = totalGp.toFixed(2);
  qs("#total-ch").textContent = totalCh;
  qs("#gpa-cell").textContent = "GPA: —";
  qs("#submit-status").textContent = "";
  if(allFilled()){
    qs("#submit-wrap").classList.remove("hidden");
  } else {
    qs("#submit-wrap").classList.add("hidden");
  }
}

async function submitForm(){
  const name = qs("#student-name").value.trim();
  const roll = qs("#roll-no").value.trim();
  if(!name || !roll){
    alert("Please enter your Name and Roll Number.");
    return;
  }
  if(!allFilled()){
    alert("Please fill Grade Point for all courses (0.00 to 4.00).");
    return;
  }
  const {gradePoints, creditHours} = collectArrays();
  const resultPy = computeGpaPyFn(gradePoints, creditHours).toJs({dict:true});
  const {gpa, total_gp, total_ch} = resultPy;
  qs("#gpa-cell").textContent = `GPA: ${gpa.toFixed ? gpa.toFixed(2) : gpa}`;
  qs("#total-gp").textContent = (total_gp.toFixed ? total_gp.toFixed(2) : total_gp);
  qs("#total-ch").textContent = total_ch;

  const grades = state.courses.map(c => ({
    course_id: c.id,
    grade_point: parseFloat(state.gradeInputs.get(c.id).value)
  }));
  const payload = {
    name, roll_no: roll, semester_id: state.semesterId, grades
  };

  try{
    const res = await fetch(`${window.API_BASE_URL}/api/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if(res.ok){
      const data = await res.json();
      qs("#submit-status").textContent = `Saved! Submission #${data.id} | GPA ${data.gpa.toFixed(2)}`;
    } else {
      const err = await res.json().catch(()=>({}));
      qs("#submit-status").textContent = `Error: ${err.detail || res.status}`;
    }
  }catch(err){
    qs("#submit-status").textContent = `Network error: ${err.message}`;
  }
}

async function start(){
  await initPy();
  qsa(".sem-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const semId = parseInt(btn.dataset.sem, 10);
      state.semesterId = semId;
      qs("#sem-title").textContent = btn.textContent;
      try{
        const courses = await fetchCourses(semId);
        state.courses = courses;
        buildTable(courses);
        show("#semester-ui");
      }catch(e){
        alert("Could not load courses. Check API_BASE_URL.");
      }
    });
  });
  qs("#submit-btn").addEventListener("click", submitForm);
}

document.addEventListener("DOMContentLoaded", start);