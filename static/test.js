// Global variables
let tasks = [];
let editingTaskId = null;
let reflectingTaskId = null;
let currentUser = null;
let currentTeam = null;
let currentFilter = 'all';
let showCompleted = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  loadTasks();
  loadTeamInfo();
  checkOverdueTasks();
  renderTasks();
});

// Task Creation
function makeTask(title, desc, date) {
  return {
    id: Date.now(),
    title,
    desc,
    date,
    done: false,
    reflection: null,
    reflectionDate: null,
    createdBy: currentUser
  };
}

// Add Task
function addTask() {
  const title = document.getElementById("taskTitle").value.trim();
  const desc = document.getElementById("taskDescription").value.trim();
  const date = document.getElementById("taskDueDate").value;

  if (!title || !date) {
    alert("Please fill in title and due date.");
    return;
  }

  tasks.push(makeTask(title, desc, date));
  closeAddModal();
  clearForm();
  saveTasks();
  renderTasks();
}

// Delete Task
function deleteTask(id) {
  if (confirm("Are you sure you want to delete this task?")) {
    tasks = tasks.filter(t => t.id !== id);
    saveTasks();
    renderTasks();
  }
}

// Toggle Task Completion
function toggleTask(id) {
  const t = tasks.find(t => t.id === id);
  if (t) {
    t.done = !t.done;
    saveTasks();
    renderTasks();
  }
}

// Open Edit Modal
function openEditModal(id) {
  const task = tasks.find(t => t.id === id);
  if (!task) return;

  editingTaskId = id;
  document.getElementById("editTaskTitle").value = task.title;
  document.getElementById("editTaskDescription").value = task.desc;
  document.getElementById("editTaskDueDate").value = task.date;
  document.getElementById("editModal").classList.add("show");
}

// Close Edit Modal
function closeEditModal() {
  editingTaskId = null;
  document.getElementById("editModal").classList.remove("show");
}

// Save Edit
function saveEdit() {
  const task = tasks.find(t => t.id === editingTaskId);
  if (!task) return;

  const title = document.getElementById("editTaskTitle").value.trim();
  const desc = document.getElementById("editTaskDescription").value.trim();
  const date = document.getElementById("editTaskDueDate").value;

  if (!title || !date) {
    alert("Please fill in title and due date.");
    return;
  }

  task.title = title;
  task.desc = desc;
  task.date = date;

  closeEditModal();
  saveTasks();
  renderTasks();
}

// Team Modal Functions
function openTeamModal() {
  displayTeamInfo();
  document.getElementById("teamModal").classList.add("show");
}

function closeTeamModal() {
  document.getElementById("teamModal").classList.remove("show");
}

function joinTeam() {
  const userName = document.getElementById("teamName").value.trim();
  const teamName = document.getElementById("teamGroupName").value.trim();

  if (!userName || !teamName) {
    alert("Please fill in both your name and team name.");
    return;
  }

  currentUser = userName;
  currentTeam = teamName;

  saveTeamInfo();
  alert(`Welcome ${userName}! You've joined team: ${teamName}`);
  displayTeamInfo();
}

function displayTeamInfo() {
  const teamInfoDiv = document.getElementById("teamInfo");
  
  if (currentUser && currentTeam) {
    teamInfoDiv.innerHTML = `
      <p><strong>Current User:</strong> ${currentUser}</p>
      <p><strong>Team:</strong> ${currentTeam}</p>
      <button onclick="leaveTeam()" class="team-btn" style="margin-top: 8px;">Leave Team</button>
    `;
  } else {
    teamInfoDiv.innerHTML = `<p style="color: #7C6F68; font-style: italic;">Not currently in a team</p>`;
  }
}

function leaveTeam() {
  if (confirm("Are you sure you want to leave the team?")) {
    currentUser = null;
    currentTeam = null;
    document.getElementById("teamName").value = "";
    document.getElementById("teamGroupName").value = "";
    saveTeamInfo();
    displayTeamInfo();
    alert("You have left the team.");
  }
}

// Reflection Modal Functions
function openReflectionModal(id) {
  const task = tasks.find(t => t.id === id);
  if (!task) return;

  reflectingTaskId = id;
  document.getElementById("reflectionTaskTitle").textContent = task.title;
  document.getElementById("reflectionTaskDate").textContent = new Date(task.date).toLocaleDateString();
  document.getElementById("reflectionText").value = task.reflection || "";
  document.getElementById("reflectionModal").classList.add("show");
}

function closeReflectionModal() {
  reflectingTaskId = null;
  document.getElementById("reflectionModal").classList.remove("show");
}

function submitReflection() {
  const task = tasks.find(t => t.id === reflectingTaskId);
  if (!task) return;

  const reflectionText = document.getElementById("reflectionText").value.trim();
  if (!reflectionText) {
    alert("Please write a reflection.");
    return;
  }

  task.reflection = reflectionText;
  task.reflectionDate = new Date().toISOString();

  closeReflectionModal();
  saveTasks();
  renderTasks();
  alert("Reflection saved!");
}

// Check for Overdue Tasks
function checkOverdueTasks() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  tasks.forEach(task => {
    const dueDate = new Date(task.date);
    dueDate.setHours(0, 0, 0, 0);

    if (!task.done && dueDate < today && !task.reflection) {
      // Task is overdue and has no reflection
      
    }
  });
}

// Clear Form
function clearForm() {
  document.getElementById("taskTitle").value = "";
  document.getElementById("taskDescription").value = "";
  document.getElementById("taskDueDate").value = "";
}

// Add Modal Functions
function openAddModal() {
  document.getElementById("addModal").classList.add("show");
}

function closeAddModal() {
  document.getElementById("addModal").classList.remove("show");
}

// Filter Functions
function filterByPriority(level) {
  currentFilter = level;
  
  // Update button styles
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');
  
  renderTasks();
}

function toggleCompletedView() {
  showCompleted = !showCompleted;
  event.target.textContent = showCompleted ? "View All" : "View Completed";
  renderTasks();
}

// Priority Calculation
function getPriorityLevel(task) {
  const due = new Date(task.date);
  const today = new Date();
  const daysUntilDue = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
  
  if (daysUntilDue <= 3) return 1;
  if (daysUntilDue <= 6) return 2;
  if (daysUntilDue <= 9) return 3;
  return 4;
}

function priorityLabel(task) {
  const due = new Date(task.date);
  const today = new Date();
  const daysUntilDue = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
  
  if (daysUntilDue < 0) return `Level 1 (OVERDUE by ${Math.abs(daysUntilDue)} days)`;
  if (daysUntilDue <= 3) return "Level 1 (Critical)";
  if (daysUntilDue <= 6) return "Level 2 (Important)";
  if (daysUntilDue <= 9) return "Level 3 (Urgent)";
  return "Level 4 (Low)";
}

function getCountdown(task) {
  const due = new Date(task.date);
  const today = new Date();
  const daysUntilDue = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
  
  if (daysUntilDue < 0) {
    return `<span class="countdown">OVERDUE by ${Math.abs(daysUntilDue)} day(s)</span>`;
  } else if (daysUntilDue === 0) {
    return `<span class="countdown">DUE TODAY!</span>`;
  } else if (daysUntilDue <= 3) {
    return `<span class="countdown">Due in ${daysUntilDue} day(s)</span>`;
  } else {
    return `<span class="countdown safe">Due in ${daysUntilDue} day(s)</span>`;
  }
}

function isOverdue(task) {
  const due = new Date(task.date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  due.setHours(0, 0, 0, 0);
  return !task.done && due < today;
}

// Render Tasks
function renderTasks() {
  const c = document.getElementById("tasksContainer");

  // Filter tasks
  let filteredTasks = tasks;
  
  if (showCompleted) {
    filteredTasks = filteredTasks.filter(t => t.done);
  }
  
  if (currentFilter !== 'all') {
    filteredTasks = filteredTasks.filter(t => getPriorityLevel(t) === currentFilter);
  }

  // Sort by priority (1-4), then by date
  filteredTasks = [...filteredTasks].sort((a, b) => {
    const priorityA = getPriorityLevel(a);
    const priorityB = getPriorityLevel(b);
    
    if (priorityA !== priorityB) {
      return priorityA - priorityB;
    }
    
    return new Date(a.date) - new Date(b.date);
  });

  // Handle empty state
  if (filteredTasks.length === 0) {
    c.innerHTML = `
      <div class="empty-state">
        <h2>No tasks found</h2>
        <p>${showCompleted ? 'No completed tasks yet!' : 'Add a task to get started!'}</p>
      </div>`;
    return;
  }

  // Render tasks
  c.innerHTML = filteredTasks.map(t => {
    const overdueClass = isOverdue(t) ? 'overdue' : '';
    const priorityClass = `priority-${getPriorityLevel(t)}`;
    
    return `
      <div class="task ${t.done ? "completed" : ""} ${overdueClass} ${priorityClass}">
        <div class="task-header">
          <button onclick="toggleTask(${t.id})">${t.done ? "✓" : "○"}</button>
          <h3>${t.title}</h3>
        </div>
        ${t.desc ? `<p>${t.desc}</p>` : ""}
        <p><strong>Due:</strong> ${new Date(t.date).toLocaleDateString()} ${getCountdown(t)}</p>
        <p><strong>Priority:</strong> ${priorityLabel(t)}</p>
        ${t.createdBy ? `<p><strong>Created by:</strong> ${t.createdBy}</p>` : ""}
        ${isOverdue(t) && !t.reflection ? `
          <p style="color: #D32F2F; font-weight: bold;">This task is overdue. Please add a reflection.</p>
        ` : ''}
        ${t.reflection ? `
          <div class="reflection">
            <strong>Reflection (${new Date(t.reflectionDate).toLocaleDateString()}):</strong>
            <p>${t.reflection}</p>
          </div>
        ` : ''}
        <div class="task-actions">
          <button onclick="openEditModal(${t.id})">Edit</button>
          <button onclick="deleteTask(${t.id})">Delete</button>
          ${isOverdue(t) ? `<button onclick="openReflectionModal(${t.id})" style="background: #FF9800;">${t.reflection ? 'Edit' : 'Add'} Reflection</button>` : ''}
        </div>
      </div>
    `;
  }).join("");
}

// Local Storage Functions
function saveTasks() {
  localStorage.setItem('tasks', JSON.stringify(tasks));
}

function loadTasks() {
  const stored = localStorage.getItem('tasks');
  if (stored) {
    tasks = JSON.parse(stored);
  }
}

function saveTeamInfo() {
  localStorage.setItem('currentUser', currentUser || '');
  localStorage.setItem('currentTeam', currentTeam || '');
}

function loadTeamInfo() {
  currentUser = localStorage.getItem('currentUser') || null;
  currentTeam = localStorage.getItem('currentTeam') || null;
  if (currentUser === '') currentUser = null;
  if (currentTeam === '') currentTeam = null;
}
