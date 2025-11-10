# Complete Code Reference (Updated)
## Daily Coding Challenge (WhatsApp) & Tech Salary Negotiation Helper (Gemini)

---

# Table of Contents

1. [Daily Coding Challenge via WhatsApp](#daily-coding-challenge)
   - [Tech Stack](#tech-stack-1)
   - [WhatsApp Bot Setup](#whatsapp-bot-setup)
   - [Problem Distribution](#problem-distribution)
   - [User Onboarding](#user-onboarding)
   - [Solution Submission](#solution-submission)
   - [Code Execution](#code-execution)
   - [Leaderboard System](#leaderboard-system)
   - [Gamification](#gamification)
   - [Database Schema](#database-schema-1)

2. [Tech Salary Negotiation Helper](#tech-salary-negotiation-helper)
   - [Tech Stack](#tech-stack-2)
   - [Offer Letter Processing](#offer-letter-processing)
   - [AI Analysis Engine (Gemini)](#ai-analysis-engine)
   - [Market Data Engine](#market-data-engine)
   - [Negotiation Script Generator](#negotiation-script-generator)
   - [Salary Database](#salary-database)
   - [Database Schema](#database-schema-2)

---

# Daily Coding Challenge

## Tech Stack {#tech-stack-1}

```json
{
  "backend": "Node.js + Express",
  "database": "PostgreSQL",
  "cache": "Redis",
  "whatsapp": "whatsapp-web.js",
  "scheduler": "node-cron",
  "code_executor": "Judge0 API / Piston API",
  "hosting": "Railway / Render / VPS"
}
```

## WhatsApp Bot Setup

```javascript
// index.js
require('dotenv').config();
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const db = require('./db');
const problemDistributor = require('./services/problemDistributor');
const commandHandler = require('./bot/commandHandler');

// Initialize WhatsApp client
const client = new Client({
  authStrategy: new LocalAuth({
    dataPath: './whatsapp-session'
  }),
  puppeteer: {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu'
    ]
  }
});

// Event: QR Code generation for authentication
client.on('qr', (qr) => {
  console.log('📱 Scan QR code to authenticate WhatsApp:');
  qrcode.generate(qr, { small: true });
});

// Event: Client is ready
client.on('ready', () => {
  console.log('✅ WhatsApp Bot is ready!');
  console.log('Starting scheduled tasks...');
  problemDistributor.startScheduler(client);
});

// Event: Authentication successful
client.on('authenticated', () => {
  console.log('🔐 Authentication successful!');
});

// Event: Authentication failure
client.on('auth_failure', (msg) => {
  console.error('❌ Authentication failed:', msg);
});

// Event: Client disconnected
client.on('disconnected', (reason) => {
  console.log('⚠️ Client was disconnected:', reason);
});

// Event: Incoming messages
client.on('message', async (message) => {
  await commandHandler.handleMessage(client, message);
});

// Initialize client
client.initialize();

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('Shutting down gracefully...');
  await client.destroy();
  process.exit(0);
});
```

## Problem Distribution

```javascript
// services/problemDistributor.js
const cron = require('node-cron');
const db = require('../db');

let scheduledTask = null;

function startScheduler(client) {
  // Schedule daily problem distribution at 9 AM
  scheduledTask = cron.schedule('0 9 * * *', async () => {
    console.log('🕐 Starting daily problem distribution...');
    await distributeDailyProblem(client);
  });
  
  console.log('⏰ Scheduler started: Daily problems at 9:00 AM');
}

async function distributeDailyProblem(client) {
  try {
    const users = await getActiveUsers();
    const problem = await getDailyProblem();
    
    console.log(`📤 Distributing problem #${problem.id} to ${users.length} users`);
    
    let successCount = 0;
    let failCount = 0;
    
    for (const user of users) {
      try {
        const chatId = user.whatsapp_number + '@c.us';
        await client.sendMessage(chatId, formatProblem(problem));
        successCount++;
        
        // Small delay to avoid rate limiting
        await sleep(500);
      } catch (error) {
        console.error(`❌ Failed to send to ${user.username}:`, error.message);
        failCount++;
      }
    }
    
    console.log(`✅ Distribution complete: ${successCount} success, ${failCount} failed`);
  } catch (error) {
    console.error('❌ Distribution error:', error);
  }
}

async function getActiveUsers() {
  const query = `
    SELECT id, whatsapp_number, username, difficulty_level
    FROM users
    WHERE is_active = true
    ORDER BY id
  `;
  
  const result = await db.query(query);
  return result.rows;
}

async function getDailyProblem() {
  const today = new Date().toISOString().split('T')[0];
  
  // Check if problem already selected for today
  let problem = await db.query(
    'SELECT p.* FROM problems p JOIN daily_problems dp ON p.id = dp.problem_id WHERE dp.date = $1',
    [today]
  );
  
  if (problem.rows.length === 0) {
    // Select random problem not used in last 30 days
    problem = await db.query(`
      SELECT * FROM problems 
      WHERE id NOT IN (
        SELECT problem_id FROM daily_problems 
        WHERE date > NOW() - INTERVAL '30 days'
      )
      ORDER BY RANDOM()
      LIMIT 1
    `);
    
    if (problem.rows.length > 0) {
      // Mark as used today
      await db.query(
        'INSERT INTO daily_problems (date, problem_id) VALUES ($1, $2)',
        [today, problem.rows[0].id]
      );
    }
  }
  
  return problem.rows[0];
}

function formatProblem(problem) {
  return `🧩 *Daily Challenge #${problem.id}*
⏱️ Difficulty: ${problem.difficulty.toUpperCase()}
🏆 Points: ${problem.points}

*${problem.title}*
${problem.description}

*Example:*
\`\`\`
Input: ${problem.example_input}
Output: ${problem.example_output}
\`\`\`

*Constraints:*
${problem.constraints}

📝 Submit: *!submit* [kode kamu]
💡 Hint: *!hint*
📊 Leaderboard: *!leaderboard*
⏭️ Skip: *!skip* (streak reset!)

Ketik *!help* untuk perintah lainnya`;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = {
  startScheduler,
  distributeDailyProblem,
  getDailyProblem,
  formatProblem
};
```

## User Onboarding

```javascript
// bot/commands/start.js
const db = require('../db');

// User state management for onboarding
const userSessions = new Map();

async function handleStart(client, message) {
  const sender = message.from;
  const contact = await message.getContact();
  const name = contact.pushname || contact.name || 'User';
  
  // Extract phone number without @c.us
  const phoneNumber = sender.replace('@c.us', '');
  
  // Check if user exists
  const existingUser = await db.query(
    'SELECT * FROM users WHERE whatsapp_number = $1',
    [phoneNumber]
  );
  
  if (existingUser.rows.length > 0) {
    const user = existingUser.rows[0];
    const welcomeBack = `👋 Welcome back, *${user.username}*! 🎉

📊 *Your Stats:*
🔥 Streak: ${user.streak} days
🎯 Points: ${user.points}
✅ Solved: ${user.total_solved} problems

Ketik *!help* untuk melihat perintah yang tersedia.`;
    
    await message.reply(welcomeBack);
    return;
  }
  
  // Start onboarding for new user
  userSessions.set(sender, { step: 'difficulty', name: name, phone: phoneNumber });
  
  const welcomeMsg = `👋 Halo *${name}*! Welcome to *Daily Coding Challenge*!

Bangun kebiasaan coding kamu dengan menyelesaikan 1 problem setiap hari 💪

Mari setup akun kamu...

*Pilih level kesulitan:*
1️⃣ Easy - Untuk pemula
2️⃣ Medium - Untuk intermediate
3️⃣ Hard - Untuk advanced

Balas dengan angka (1, 2, atau 3)`;
  
  await message.reply(welcomeMsg);
}

async function handleOnboardingResponse(client, message) {
  const sender = message.from;
  const session = userSessions.get(sender);
  
  if (!session) return false; // Not in onboarding flow
  
  const text = message.body.trim();
  
  if (session.step === 'difficulty') {
    const difficulties = { '1': 'easy', '2': 'medium', '3': 'hard' };
    const difficulty = difficulties[text];
    
    if (!difficulty) {
      await message.reply('❌ Pilihan tidak valid. Balas dengan 1, 2, atau 3');
      return true;
    }
    
    session.difficulty = difficulty;
    session.step = 'language';
    
    const langMsg = `✅ Difficulty set to *${difficulty.toUpperCase()}*

*Pilih bahasa programming favorit:*
1️⃣ Python
2️⃣ JavaScript
3️⃣ Java
4️⃣ C++
5️⃣ Go

Balas dengan angka (1-5)`;
    
    await message.reply(langMsg);
    return true;
  }
  
  if (session.step === 'language') {
    const languages = {
      '1': 'python',
      '2': 'javascript',
      '3': 'java',
      '4': 'cpp',
      '5': 'go'
    };
    const language = languages[text];
    
    if (!language) {
      await message.reply('❌ Pilihan tidak valid. Balas dengan 1-5');
      return true;
    }
    
    session.language = language;
    session.step = 'time';
    
    const timeMsg = `✅ Language set to *${language.toUpperCase()}*

*Jam berapa kamu mau terima daily challenge?*
Format: HH:MM (24-jam)
Contoh: 09:00 atau 14:30`;
    
    await message.reply(timeMsg);
    return true;
  }
  
  if (session.step === 'time') {
    const timeRegex = /^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$/;
    
    if (!timeRegex.test(text)) {
      await message.reply('❌ Format waktu salah. Gunakan HH:MM (contoh: 09:00)');
      return true;
    }
    
    session.notificationTime = text;
    
    // Create user account
    try {
      await db.query(`
        INSERT INTO users (
          whatsapp_number, username, difficulty_level,
          preferred_language, notification_time, timezone
        ) VALUES ($1, $2, $3, $4, $5, $6)
      `, [
        session.phone,
        session.name,
        session.difficulty,
        session.language,
        session.notificationTime,
        'WIB'
      ]);
      
      const successMsg = `🎉 *Setup Complete!*

📋 *Profil Kamu:*
👤 Username: ${session.name}
📊 Difficulty: ${session.difficulty}
💻 Language: ${session.language}
⏰ Daily challenge: ${session.notificationTime} WIB

Challenge pertama akan dikirim besok!
Ketik *!help* untuk melihat apa yang bisa kamu lakukan.

Happy coding! 🚀`;
      
      await message.reply(successMsg);
      
      // Clear session
      userSessions.delete(sender);
    } catch (error) {
      console.error('Error creating user:', error);
      await message.reply('❌ Terjadi kesalahan. Silakan coba lagi dengan !start');
      userSessions.delete(sender);
    }
    
    return true;
  }
  
  return false;
}

module.exports = {
  handleStart,
  handleOnboardingResponse
};
```

## Solution Submission

```javascript
// bot/commands/submit.js
const db = require('../db');
const { executeCode } = require('../services/codeExecutor');

async function handleSubmit(client, message) {
  const text = message.body;
  const sender = message.from;
  const phoneNumber = sender.replace('@c.us', '');
  
  // Extract code (everything after !submit)
  const code = text.replace(/^!submit\s+/i, '').trim();
  
  if (!code || code === '!submit') {
    const helpMsg = `❌ Silakan kirim kode kamu setelah !submit

*Contoh:*
\`\`\`
!submit
def solution(nums):
    return sum(nums)
\`\`\``;
    
    await message.reply(helpMsg);
    return;
  }
  
  // Get user info
  const userResult = await db.query(
    'SELECT * FROM users WHERE whatsapp_number = $1',
    [phoneNumber]
  );
  
  if (userResult.rows.length === 0) {
    await message.reply('❌ Kamu belum terdaftar. Ketik *!start* untuk mendaftar.');
    return;
  }
  
  const user = userResult.rows[0];
  
  // Get today's problem
  const today = new Date().toISOString().split('T')[0];
  const problemResult = await db.query(`
    SELECT p.* FROM problems p
    JOIN daily_problems dp ON p.id = dp.problem_id
    WHERE dp.date = $1
  `, [today]);
  
  if (problemResult.rows.length === 0) {
    await message.reply('❌ Belum ada problem untuk hari ini. Coba lagi besok!');
    return;
  }
  
  const problem = problemResult.rows[0];
  
  // Check if already solved today
  const solvedCheck = await db.query(`
    SELECT * FROM submissions
    WHERE user_id = $1 AND problem_id = $2 
    AND status = 'accepted'
    AND DATE(submitted_at) = $3
  `, [user.id, problem.id, today]);
  
  if (solvedCheck.rows.length > 0) {
    await message.reply('✅ Kamu sudah menyelesaikan problem hari ini!\nKembali besok untuk challenge baru.');
    return;
  }
  
  // Show "running..." message
  await message.reply('⏳ Running your code...');
  
  try {
    // Execute code
    const result = await executeCode({
      code: code,
      language: user.preferred_language,
      testCases: problem.test_cases
    });
    
    if (result.allPassed) {
      // Calculate points
      const points = calculatePoints(problem, result.avgTime, user.streak);
      
      // Update user stats
      await db.query(`
        UPDATE users
        SET 
          points = points + $1,
          streak = CASE 
            WHEN last_solved_date = CURRENT_DATE - INTERVAL '1 day' 
            THEN streak + 1
            ELSE 1
          END,
          max_streak = GREATEST(max_streak, 
            CASE 
              WHEN last_solved_date = CURRENT_DATE - INTERVAL '1 day' 
              THEN streak + 1
              ELSE 1
            END
          ),
          total_solved = total_solved + 1,
          last_solved_date = CURRENT_DATE
        WHERE id = $2
        RETURNING streak
      `, [points, user.id]);
      
      const updatedUser = await db.query('SELECT * FROM users WHERE id = $1', [user.id]);
      const newStreak = updatedUser.rows[0].streak;
      
      // Record submission
      await db.query(`
        INSERT INTO submissions (
          user_id, problem_id, code, language, 
          status, execution_time, submitted_at
        ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
      `, [
        user.id, problem.id, code, user.preferred_language,
        'accepted', result.avgTime
      ]);
      
      // Get updated rank
      const rankResult = await db.query(`
        SELECT COUNT(*) + 1 as rank
        FROM users
        WHERE points > $1 AND is_active = true
      `, [updatedUser.rows[0].points]);
      
      const rank = rankResult.rows[0].rank;
      
      const successMsg = `✅ *Correct Solution!*

⚡ Execution Time: ${result.avgTime.toFixed(2)}ms
🎯 Points Earned: +${points}
🔥 Current Streak: ${newStreak} days
💰 Total Points: ${updatedUser.rows[0].points}
🏆 Your Rank: #${rank}

Amazing work! Keep the streak going! 🚀`;
      
      await message.reply(successMsg);
      
      // Check for new badges
      await checkAndAwardBadges(client, message, user.id);
      
    } else {
      // Show first failed test case
      const failedTest = result.failedTests[0];
      
      // Record failed submission
      await db.query(`
        INSERT INTO submissions (
          user_id, problem_id, code, language,
          status, submitted_at
        ) VALUES ($1, $2, $3, $4, $5, NOW())
      `, [
        user.id, problem.id, code, user.preferred_language,
        'wrong_answer'
      ]);
      
      const failMsg = `❌ *Failed ${result.failedTests.length}/${result.totalTests} test case(s)*

*Test Case #${failedTest.id}:*
Input: \`${failedTest.input}\`
Expected: \`${failedTest.expected}\`
Got: \`${failedTest.actual}\`

💡 Tip: ${getHintForError()}

Try again! No penalty for retrying. 💪`;
      
      await message.reply(failMsg);
    }
  } catch (error) {
    console.error('Execution error:', error);
    
    const errorMsg = `❌ *Execution Error*

${error.message}

Please check your code and try again.`;
    
    await message.reply(errorMsg);
  }
}

function calculatePoints(problem, executionTime, currentStreak) {
  let basePoints = problem.points;
  
  // Speed bonus
  if (problem.average_time && executionTime < problem.average_time * 0.5) {
    basePoints *= 1.5;
  } else if (problem.average_time && executionTime < problem.average_time * 0.75) {
    basePoints *= 1.2;
  }
  
  // Streak multiplier (max 60% bonus at 30 day streak)
  const streakMultiplier = 1 + (Math.min(currentStreak, 30) * 0.02);
  
  return Math.floor(basePoints * streakMultiplier);
}

function getHintForError() {
  const hints = [
    'Check your edge cases',
    'Are you handling empty inputs?',
    'Double-check your loop conditions',
    'Consider using a different data structure',
    'Review the problem constraints'
  ];
  
  return hints[Math.floor(Math.random() * hints.length)];
}

async function checkAndAwardBadges(client, message, userId) {
  // Implementation from gamification section
  // Will check and notify user of new badges
}

module.exports = { handleSubmit };
```

## Code Execution

```javascript
// services/codeExecutor.js
const axios = require('axios');

const JUDGE0_API_URL = 'https://judge0-ce.p.rapidapi.com';
const JUDGE0_API_KEY = process.env.JUDGE0_API_KEY;

const LANGUAGE_IDS = {
  'python': 71,      // Python 3
  'javascript': 63,  // JavaScript (Node.js)
  'java': 62,        // Java
  'cpp': 54,         // C++ (GCC)
  'go': 60          // Go
};

async function executeCode({ code, language, testCases }) {
  const results = [];
  
  for (let i = 0; i < testCases.length; i++) {
    const testCase = testCases[i];
    
    try {
      const result = await runSingleTest(code, language, testCase);
      results.push({
        id: i + 1,
        passed: result.passed,
        executionTime: result.time,
        memory: result.memory,
        input: testCase.input,
        expected: testCase.expected_output,
        actual: result.stdout?.trim()
      });
    } catch (error) {
      results.push({
        id: i + 1,
        passed: false,
        error: error.message,
        input: testCase.input,
        expected: testCase.expected_output,
        actual: null
      });
    }
  }
  
  const failedTests = results.filter(r => !r.passed);
  const avgTime = results.reduce((sum, r) => sum + (r.executionTime || 0), 0) / results.length;
  
  return {
    allPassed: failedTests.length === 0,
    totalTests: results.length,
    passedTests: results.length - failedTests.length,
    failedTests: failedTests,
    avgTime: avgTime,
    results: results
  };
}

async function runSingleTest(code, language, testCase) {
  // Create submission
  const submissionResponse = await axios.post(
    `${JUDGE0_API_URL}/submissions?base64_encoded=false&wait=true`,
    {
      source_code: code,
      language_id: LANGUAGE_IDS[language],
      stdin: testCase.input,
      expected_output: testCase.expected_output,
      cpu_time_limit: 2,
      memory_limit: 128000
    },
    {
      headers: {
        'content-type': 'application/json',
        'X-RapidAPI-Key': JUDGE0_API_KEY,
        'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
      }
    }
  );
  
  const submission = submissionResponse.data;
  const statusId = submission.status.id;
  
  // Status IDs: 3=Accepted, 4=Wrong Answer, 5=Time Limit, 6=Compilation Error, 11=Runtime Error
  
  return {
    passed: statusId === 3,
    time: parseFloat(submission.time) * 1000, // Convert to ms
    memory: submission.memory,
    stdout: submission.stdout,
    stderr: submission.stderr,
    statusId: statusId,
    statusDescription: submission.status.description
  };
}

module.exports = { executeCode };
```

## Leaderboard System

```javascript
// bot/commands/leaderboard.js
const db = require('../db');

async function handleLeaderboard(client, message) {
  const text = message.body.toLowerCase();
  
  let period = 'weekly';
  if (text.includes('daily')) period = 'daily';
  else if (text.includes('monthly')) period = 'monthly';
  else if (text.includes('alltime') || text.includes('all')) period = 'alltime';
  
  const sender = message.from;
  const phoneNumber = sender.replace('@c.us', '');
  
  let leaderboardData;
  let userRank;
  
  switch(period) {
    case 'daily':
      leaderboardData = await getDailyLeaderboard();
      userRank = await getUserDailyRank(phoneNumber);
      break;
    case 'monthly':
      leaderboardData = await getMonthlyLeaderboard();
      userRank = await getUserMonthlyRank(phoneNumber);
      break;
    case 'alltime':
      leaderboardData = await getAllTimeLeaderboard();
      userRank = await getUserAllTimeRank(phoneNumber);
      break;
    default:
      leaderboardData = await getWeeklyLeaderboard();
      userRank = await getUserWeeklyRank(phoneNumber);
  }
  
  const leaderboardText = formatLeaderboard(leaderboardData, period, userRank);
  await message.reply(leaderboardText);
}

async function getWeeklyLeaderboard() {
  const query = `
    SELECT 
      u.username,
      u.points,
      u.streak,
      COUNT(DISTINCT s.id) as solved_this_week
    FROM users u
    LEFT JOIN submissions s ON u.id = s.user_id 
      AND s.status = 'accepted'
      AND s.submitted_at > NOW() - INTERVAL '7 days'
    WHERE u.is_active = true
    GROUP BY u.id, u.username, u.points, u.streak
    ORDER BY u.points DESC
    LIMIT 10
  `;
  
  const result = await db.query(query);
  return result.rows;
}

async function getDailyLeaderboard() {
  const query = `
    SELECT 
      u.username,
      MIN(s.submitted_at) as first_solve_time
    FROM users u
    JOIN submissions s ON u.id = s.user_id
    WHERE 
      s.status = 'accepted'
      AND DATE(s.submitted_at) = CURRENT_DATE
    GROUP BY u.id, u.username
    ORDER BY first_solve_time
    LIMIT 10
  `;
  
  const result = await db.query(query);
  return result.rows;
}

async function getMonthlyLeaderboard() {
  const query = `
    SELECT 
      u.username,
      u.points,
      COUNT(DISTINCT s.id) as solved_this_month
    FROM users u
    LEFT JOIN submissions s ON u.id = s.user_id
      AND s.status = 'accepted'
      AND s.submitted_at > DATE_TRUNC('month', NOW())
    WHERE u.is_active = true
    GROUP BY u.id, u.username, u.points
    ORDER BY solved_this_month DESC, u.points DESC
    LIMIT 10
  `;
  
  const result = await db.query(query);
  return result.rows;
}

async function getAllTimeLeaderboard() {
  const query = `
    SELECT 
      u.username,
      u.points,
      u.streak,
      u.total_solved
    FROM users u
    WHERE u.is_active = true
    ORDER BY u.points DESC
    LIMIT 10
  `;
  
  const result = await db.query(query);
  return result.rows;
}

async function getUserWeeklyRank(phoneNumber) {
  const result = await db.query(`
    SELECT rank FROM (
      SELECT 
        u.whatsapp_number,
        RANK() OVER (ORDER BY u.points DESC) as rank
      FROM users u
      WHERE u.is_active = true
    ) ranked
    WHERE whatsapp_number = $1
  `, [phoneNumber]);
  
  return result.rows[0]?.rank || 'Unranked';
}

async function getUserDailyRank(phoneNumber) {
  const result = await db.query(`
    SELECT rank FROM (
      SELECT 
        u.whatsapp_number,
        RANK() OVER (ORDER BY MIN(s.submitted_at)) as rank
      FROM users u
      JOIN submissions s ON u.id = s.user_id
      WHERE 
        s.status = 'accepted'
        AND DATE(s.submitted_at) = CURRENT_DATE
      GROUP BY u.id, u.whatsapp_number
    ) ranked
    WHERE whatsapp_number = $1
  `, [phoneNumber]);
  
  return result.rows[0]?.rank || 'Unranked';
}

async function getUserMonthlyRank(phoneNumber) {
  const result = await db.query(`
    SELECT rank FROM (
      SELECT 
        u.whatsapp_number,
        RANK() OVER (ORDER BY COUNT(DISTINCT s.id) DESC, u.points DESC) as rank
      FROM users u
      LEFT JOIN submissions s ON u.id = s.user_id
        AND s.status = 'accepted'
        AND s.submitted_at > DATE_TRUNC('month', NOW())
      WHERE u.is_active = true
      GROUP BY u.id, u.whatsapp_number, u.points
    ) ranked
    WHERE whatsapp_number = $1
  `, [phoneNumber]);
  
  return result.rows[0]?.rank || 'Unranked';
}

async function getUserAllTimeRank(phoneNumber) {
  return await getUserWeeklyRank(phoneNumber); // Same as weekly for all-time
}

function formatLeaderboard(data, period, userRank) {
  const periodTitle = {
    'daily': 'Daily',
    'weekly': 'Weekly',
    'monthly': 'Monthly',
    'alltime': 'All-Time'
  }[period] || 'Weekly';
  
  let text = `🏆 *${periodTitle} Leaderboard*\n\n`;
  
  data.forEach((user, index) => {
    const emoji = getRankEmoji(index + 1);
    let stats = '';
    
    if (period === 'daily') {
      const time = new Date(user.first_solve_time);
      stats = `⏱️ ${time.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (period === 'monthly') {
      stats = `🎯 ${user.solved_this_month} solved | ${user.points} pts`;
    } else {
      stats = `🎯 ${user.points} pts | 🔥 ${user.streak || 0} days`;
    }
    
    text += `${emoji} *${user.username}*\n   ${stats}\n\n`;
  });
  
  text += `━━━━━━━━━━━━━━━\n`;
  text += `📍 Your rank: *#${userRank}*\n\n`;
  text += `_Ketik !stats untuk statistik detail_`;
  
  return text;
}

function getRankEmoji(rank) {
  switch(rank) {
    case 1: return '🥇';
    case 2: return '🥈';
    case 3: return '🥉';
    default: return `${rank}.`;
  }
}

module.exports = { handleLeaderboard };
```

## Gamification

```javascript
// services/gamification.js
const db = require('../db');

const BADGES = {
  'first_blood': {
    name: '🎯 First Blood',
    emoji: '🎯',
    description: 'Solved your first problem',
    condition: (user) => user.total_solved >= 1
  },
  'week_warrior': {
    name: '🔥 Week Warrior',
    emoji: '🔥',
    description: 'Maintained 7-day streak',
    condition: (user) => user.streak >= 7
  },
  'month_master': {
    name: '🌟 Month Master',
    emoji: '🌟',
    description: 'Maintained 30-day streak',
    condition: (user) => user.streak >= 30
  },
  'speed_demon': {
    name: '⚡ Speed Demon',
    emoji: '⚡',
    description: 'Solved 10 problems faster than average',
    requiresQuery: true
  },
  'century_club': {
    name: '💯 Century Club',
    emoji: '💯',
    description: 'Solved 100 problems',
    condition: (user) => user.total_solved >= 100
  },
  'early_bird': {
    name: '🌅 Early Bird',
    emoji: '🌅',
    description: 'Solved problems before 8 AM 10 times',
    requiresQuery: true
  },
  'night_owl': {
    name: '🦉 Night Owl',
    emoji: '🦉',
    description: 'Solved problems after 10 PM 10 times',
    requiresQuery: true
  }
};

async function checkAndAwardBadges(userId) {
  // Get user data
  const userResult = await db.query(
    'SELECT * FROM users WHERE id = $1',
    [userId]
  );
  
  const user = userResult.rows[0];
  
  // Get current badges
  const statsResult = await db.query(
    'SELECT badges FROM user_stats WHERE user_id = $1',
    [userId]
  );
  
  let currentBadges = [];
  if (statsResult.rows.length > 0 && statsResult.rows[0].badges) {
    currentBadges = statsResult.rows[0].badges;
  } else {
    // Initialize user_stats if not exists
    await db.query(
      'INSERT INTO user_stats (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING',
      [userId]
    );
  }
  
  const newBadges = [];
  
  // Check each badge condition
  for (const [badgeId, badge] of Object.entries(BADGES)) {
    if (currentBadges.includes(badgeId)) continue;
    
    let earned = false;
    
    if (badge.requiresQuery) {
      earned = await checkBadgeWithQuery(userId, badgeId);
    } else if (badge.condition) {
      earned = badge.condition(user);
    }
    
    if (earned) {
      newBadges.push({ id: badgeId, ...badge });
      currentBadges.push(badgeId);
    }
  }
  
  // Update badges in database
  if (newBadges.length > 0) {
    await db.query(
      'UPDATE user_stats SET badges = $1 WHERE user_id = $2',
      [JSON.stringify(currentBadges), userId]
    );
  }
  
  return newBadges;
}

async function checkBadgeWithQuery(userId, badgeId) {
  if (badgeId === 'speed_demon') {
    const result = await db.query(`
      SELECT COUNT(*) as fast_solves
      FROM submissions s
      JOIN problems p ON s.problem_id = p.id
      WHERE s.user_id = $1 
      AND s.execution_time < p.average_time * 0.75
      AND p.average_time IS NOT NULL
    `, [userId]);
    return result.rows[0].fast_solves >= 10;
  }
  
  if (badgeId === 'early_bird') {
    const result = await db.query(`
      SELECT COUNT(*) as early_solves
      FROM submissions
      WHERE user_id = $1
      AND EXTRACT(HOUR FROM submitted_at) < 8
      AND status = 'accepted'
    `, [userId]);
    return result.rows[0].early_solves >= 10;
  }
  
  if (badgeId === 'night_owl') {
    const result = await db.query(`
      SELECT COUNT(*) as late_solves
      FROM submissions
      WHERE user_id = $1
      AND EXTRACT(HOUR FROM submitted_at) >= 22
      AND status = 'accepted'
    `, [userId]);
    return result.rows[0].late_solves >= 10;
  }
  
  return false;
}

module.exports = {
  checkAndAwardBadges,
  BADGES
};
```

## Command Handler

```javascript
// bot/commandHandler.js
const startCmd = require('./commands/start');
const submitCmd = require('./commands/submit');
const leaderboardCmd = require('./commands/leaderboard');

async function handleMessage(client, message) {
  // Ignore group messages
  if (message.from.includes('@g.us')) {
    return;
  }
  
  // Ignore own messages
  if (message.fromMe) {
    return;
  }
  
  const text = message.body.trim();
  
  try {
    // Check if user is in onboarding flow
    const inOnboarding = await startCmd.handleOnboardingResponse(client, message);
    if (inOnboarding) return;
    
    // Command routing
    if (text.toLowerCase().startsWith('!start') || text.toLowerCase() === 'start') {
      await startCmd.handleStart(client, message);
    } 
    else if (text.toLowerCase().startsWith('!submit')) {
      await submitCmd.handleSubmit(client, message);
    } 
    else if (text.toLowerCase().startsWith('!leaderboard') || text.toLowerCase().startsWith('!lb')) {
      await leaderboardCmd.handleLeaderboard(client, message);
    } 
    else if (text.toLowerCase().startsWith('!hint')) {
      await handleHint(client, message);
    } 
    else if (text.toLowerCase().startsWith('!stats')) {
      await handleStats(client, message);
    } 
    else if (text.toLowerCase().startsWith('!skip')) {
      await handleSkip(client, message);
    } 
    else if (text.toLowerCase().startsWith('!help')) {
      await handleHelp(client, message);
    }
  } catch (error) {
    console.error('Error handling message:', error);
    await message.reply('❌ Terjadi kesalahan. Silakan coba lagi.');
  }
}

async function handleHelp(client, message) {
  const helpText = `*📚 Perintah Yang Tersedia:*

*!start* - Daftar akun baru
*!submit [kode]* - Submit solusi kamu
*!hint* - Dapatkan hint untuk problem hari ini
*!leaderboard* - Lihat leaderboard
*!stats* - Lihat statistik kamu
*!skip* - Skip challenge hari ini
*!help* - Tampilkan pesan ini

_Happy coding! 🚀_`;
  
  await message.reply(helpText);
}

async function handleHint(client, message) {
  // Implementation for hint feature
  await message.reply('💡 Hint feature coming soon!');
}

async function handleStats(client, message) {
  // Implementation for stats feature
  await message.reply('📊 Stats feature coming soon!');
}

async function handleSkip(client, message) {
  // Implementation for skip feature
  await message.reply('⏭️ Skip feature coming soon!');
}

module.exports = { handleMessage };
```

## Database Schema {#database-schema-1}

```sql
-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  whatsapp_number VARCHAR(20) UNIQUE NOT NULL,
  username VARCHAR(100),
  preferred_language VARCHAR(20) DEFAULT 'python',
  difficulty_level VARCHAR(10) DEFAULT 'medium',
  timezone VARCHAR(50) DEFAULT 'WIB',
  notification_time TIME DEFAULT '09:00:00',
  points INT DEFAULT 0,
  streak INT DEFAULT 0,
  max_streak INT DEFAULT 0,
  total_solved INT DEFAULT 0,
  last_solved_date DATE,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Problems table
CREATE TABLE problems (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  difficulty VARCHAR(10) NOT NULL,
  points INT NOT NULL,
  test_cases JSONB NOT NULL,
  example_input TEXT,
  example_output TEXT,
  constraints TEXT,
  hints JSONB,
  tags VARCHAR(100)[],
  average_time FLOAT,
  acceptance_rate FLOAT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Daily problems tracking
CREATE TABLE daily_problems (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL UNIQUE,
  problem_id INT REFERENCES problems(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Submissions table
CREATE TABLE submissions (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  problem_id INT REFERENCES problems(id),
  code TEXT NOT NULL,
  language VARCHAR(20) NOT NULL,
  status VARCHAR(20) NOT NULL,
  execution_time FLOAT,
  memory_used INT,
  submitted_at TIMESTAMP DEFAULT NOW()
);

-- User statistics table
CREATE TABLE user_stats (
  user_id INT PRIMARY KEY REFERENCES users(id),
  total_solved INT DEFAULT 0,
  easy_solved INT DEFAULT 0,
  medium_solved INT DEFAULT 0,
  hard_solved INT DEFAULT 0,
  max_streak INT DEFAULT 0,
  badges JSONB DEFAULT '[]',
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_whatsapp ON users(whatsapp_number);
CREATE INDEX idx_users_points ON users(points DESC);
CREATE INDEX idx_submissions_user_id ON submissions(user_id);
CREATE INDEX idx_submissions_problem_id ON submissions(problem_id);
CREATE INDEX idx_submissions_date ON submissions(submitted_at DESC);
CREATE INDEX idx_daily_problems_date ON daily_problems(date DESC);
```

---

# Tech Salary Negotiation Helper

## Tech Stack {#tech-stack-2}

```json
{
  "frontend": "React + TailwindCSS + Vite",
  "backend": "Python FastAPI",
  "database": "PostgreSQL",
  "ai": "Google Gemini 2.0 Flash",
  "ocr": "Google Cloud Vision API / Tesseract",
  "analytics": "Pandas + NumPy",
  "deployment": "Vercel (frontend) + Railway (backend)"
}
```

## Offer Letter Processing

```python
# services/offer_parser.py
import re
import PyPDF2
from io import BytesIO
from typing import Dict, Optional
import google.generativeai as genai
import os

class OfferLetterParser:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def parse_pdf(self, file_bytes: bytes) -> Dict:
        """Extract text from PDF and parse key information"""
        try:
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Use Gemini to extract structured data
            extracted_data = await self.extract_with_ai(text)
            
            return extracted_data
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    async def extract_with_ai(self, text: str) -> Dict:
        """Use Gemini to extract structured information"""
        prompt = f"""
Extract the following information from this job offer letter and return it as JSON.
If information is not found, use null.

Offer letter text:
{text}

Extract:
- company: Company name
- job_title: Job title/position
- location: Work location
- base_salary: Annual base salary (number only, no currency symbol)
- bonus: Annual bonus or target bonus (number only)
- equity: Equity grant details (RSUs, options, etc.)
- equity_value: Estimated annual equity value (number)
- start_date: Expected start date
- benefits: List of benefits mentioned

Return ONLY valid JSON, no other text or markdown formatting.
"""
        
        response = self.model.generate_content(prompt)
        json_text = response.text.strip()
        
        # Remove markdown code blocks if present
        json_text = re.sub(r'```json\n?|\n?```', '', json_text)
        
        import json
        return json.loads(json_text)
```

## AI Analysis Engine

```python
# services/salary_analyzer.py
import google.generativeai as genai
from typing import Dict
import os
from .market_data import MarketDataService

class SalaryAnalyzer:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.market_service = MarketDataService()
    
    async def analyze_offer(self, offer_data: Dict) -> Dict:
        """Comprehensive analysis of job offer"""
        
        # Get market data
        market_data = await self.market_service.get_market_data(
            job_title=offer_data['job_title'],
            location=offer_data['location'],
            years_experience=offer_data.get('years_experience', 0),
            tech_stack=offer_data.get('tech_stack', [])
        )
        
        # Calculate total compensation
        total_comp = self._calculate_total_comp(offer_data)
        
        # Determine verdict
        verdict = self._determine_verdict(total_comp, market_data)
        
        # Generate AI analysis using Gemini
        ai_analysis = await self._generate_ai_analysis(
            offer_data, 
            market_data, 
            verdict
        )
        
        return {
            'offer_data': offer_data,
            'market_data': market_data,
            'total_compensation': total_comp,
            'verdict': verdict,
            'analysis': ai_analysis,
            'negotiation_room': self._calculate_negotiation_room(
                total_comp, 
                market_data
            ),
            'leverage_points': self._extract_leverage_points(
                offer_data, 
                market_data
            ),
            'recommendations': await self._generate_recommendations(
                offer_data,
                market_data,
                verdict
            )
        }
    
    def _calculate_total_comp(self, offer_data: Dict) -> int:
        """Calculate total annual compensation"""
        base = offer_data.get('base_salary', 0)
        bonus = offer_data.get('bonus', 0)
        equity = offer_data.get('equity_value', 0)
        
        return base + bonus + equity
    
    def _determine_verdict(self, total_comp: int, market_data: Dict) -> str:
        """Determine if offer is competitive"""
        p25 = market_data.get('p25', 0)
        p50 = market_data.get('p50', 0)
        p75 = market_data.get('p75', 0)
        p90 = market_data.get('p90', 0)
        
        if total_comp < p25:
            return "SIGNIFICANTLY_UNDERPAID"
        elif total_comp < p50:
            return "UNDERPAID"
        elif total_comp < p75:
            return "FAIR"
        elif total_comp < p90:
            return "COMPETITIVE"
        else:
            return "EXCELLENT"
    
    async def _generate_ai_analysis(
        self, 
        offer_data: Dict, 
        market_data: Dict,
        verdict: str
    ) -> str:
        """Generate detailed AI analysis using Gemini"""
        
        company_tier = self._get_company_tier(offer_data.get('company', ''))
        
        prompt = f"""
You are a senior tech recruiter and compensation expert. Analyze this job offer comprehensively.

**Offer Details:**
- Position: {offer_data.get('job_title')}
- Company: {offer_data.get('company')} ({company_tier})
- Location: {offer_data.get('location')}
- Base Salary: ${offer_data.get('base_salary', 0):,}
- Bonus: ${offer_data.get('bonus', 0):,}
- Equity: {offer_data.get('equity', 'Not specified')}
- Years of Experience: {offer_data.get('years_experience', 'Not specified')}
- Tech Stack: {', '.join(offer_data.get('tech_stack', []))}

**Market Data:**
- Market P25: ${market_data.get('p25', 0):,}
- Market P50 (median): ${market_data.get('p50', 0):,}
- Market P75: ${market_data.get('p75', 0):,}
- Market P90: ${market_data.get('p90', 0):,}
- Assessment: {verdict}
- Sample Size: {market_data.get('sample_size', 0)} data points

Provide a detailed analysis covering:

1. **Overall Assessment**: Is this offer competitive? Why or why not?

2. **Strengths**: What are the strong points of this offer?

3. **Concerns**: What are potential red flags or weak points?

4. **Market Positioning**: Where does this offer stand compared to market rates?

5. **Negotiation Leverage**: What specific points can be used to negotiate?

6. **Non-Salary Opportunities**: What else could be negotiated besides base salary?

7. **Risk Assessment**: Any risks with this offer (company stability, equity value, etc.)?

Be specific, data-driven, and actionable. Format your response with clear sections.
"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _calculate_negotiation_room(
        self, 
        current_comp: int, 
        market_data: Dict
    ) -> Dict:
        """Calculate realistic negotiation targets"""
        p75 = market_data.get('p75', 0)
        p90 = market_data.get('p90', 0)
        
        # Conservative target: P75
        conservative = max(current_comp * 1.05, p75)
        
        # Aggressive target: P90
        aggressive = p90
        
        # Realistic target: midpoint
        realistic = (conservative + aggressive) / 2
        
        return {
            'conservative': int(conservative),
            'realistic': int(realistic),
            'aggressive': int(aggressive),
            'percentage_increase': {
                'conservative': round(((conservative / current_comp) - 1) * 100, 1),
                'realistic': round(((realistic / current_comp) - 1) * 100, 1),
                'aggressive': round(((aggressive / current_comp) - 1) * 100, 1)
            }
        }
    
    def _extract_leverage_points(
        self, 
        offer_data: Dict, 
        market_data: Dict
    ) -> list:
        """Extract specific leverage points for negotiation"""
        leverage_points = []
        
        # Market data leverage
        if market_data.get('p50', 0) > offer_data.get('base_salary', 0):
            difference = market_data['p50'] - offer_data['base_salary']
            leverage_points.append({
                'type': 'market_rate',
                'description': f"Market median is ${difference:,} higher than offer",
                'strength': 'strong'
            })
        
        # Tech stack premium
        hot_tech = ['rust', 'golang', 'kubernetes', 'ai', 'ml', 'blockchain']
        user_tech = [t.lower() for t in offer_data.get('tech_stack', [])]
        
        if any(tech in user_tech for tech in hot_tech):
            leverage_points.append({
                'type': 'tech_premium',
                'description': "Specialized in high-demand technologies",
                'strength': 'medium'
            })
        
        # Experience
        if offer_data.get('years_experience', 0) >= 5:
            leverage_points.append({
                'type': 'experience',
                'description': f"{offer_data['years_experience']}+ years of experience",
                'strength': 'medium'
            })
        
        # Competing offers
        if offer_data.get('has_competing_offers'):
            leverage_points.append({
                'type': 'competition',
                'description': "Multiple offers in hand",
                'strength': 'strong'
            })
        
        return leverage_points
    
    async def _generate_recommendations(
        self,
        offer_data: Dict,
        market_data: Dict,
        verdict: str
    ) -> list:
        """Generate actionable recommendations"""
        recommendations = []
        
        if verdict in ['SIGNIFICANTLY_UNDERPAID', 'UNDERPAID']:
            recommendations.append({
                'priority': 'high',
                'action': 'negotiate_base',
                'description': 'Negotiate base salary increase',
                'target': market_data.get('p75')
            })
        
        if not offer_data.get('equity_value'):
            recommendations.append({
                'priority': 'medium',
                'action': 'clarify_equity',
                'description': 'Request equity grant details and valuation'
            })
        
        if not offer_data.get('bonus'):
            recommendations.append({
                'priority': 'medium',
                'action': 'negotiate_bonus',
                'description': 'Negotiate performance bonus or sign-on bonus'
            })
        
        recommendations.append({
            'priority': 'low',
            'action': 'benefits_review',
            'description': 'Review and negotiate non-salary benefits'
        })
        
        return recommendations
    
    def _get_company_tier(self, company: str) -> str:
        """Determine company tier"""
        faang = ['google', 'amazon', 'meta', 'apple', 'netflix', 'microsoft']
        
        if any(f in company.lower() for f in faang):
            return 'FAANG'
        
        return 'Standard'
```

## Market Data Engine

```python
# services/market_data.py
from typing import Dict, List
import asyncpg
import os
from datetime import datetime, timedelta

class MarketDataService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
    
    async def get_market_data(
        self,
        job_title: str,
        location: str,
        years_experience: int,
        tech_stack: List[str]
    ) -> Dict:
        """Query salary database for market data"""
        
        # Normalize inputs
        normalized_title = self._normalize_job_title(job_title)
        location_tier = self._get_location_tier(location)
        col_multiplier = self._get_col_multiplier(location)
        
        # Connect to database
        conn = await asyncpg.connect(self.db_url)
        
        try:
            # Query market data
            query = """
            SELECT 
                percentile_cont(0.10) WITHIN GROUP (ORDER BY total_comp) as p10,
                percentile_cont(0.25) WITHIN GROUP (ORDER BY total_comp) as p25,
                percentile_cont(0.50) WITHIN GROUP (ORDER BY total_comp) as p50,
                percentile_cont(0.75) WITHIN GROUP (ORDER BY total_comp) as p75,
                percentile_cont(0.90) WITHIN GROUP (ORDER BY total_comp) as p90,
                COUNT(*) as sample_size,
                AVG(base_salary) as avg_base,
                AVG(bonus) as avg_bonus,
                AVG(equity_value) as avg_equity
            FROM salary_data
            WHERE 
                normalized_title = $1
                AND years_experience BETWEEN $2 - 2 AND $2 + 2
                AND location_tier = $3
                AND submitted_date > $4
                AND is_verified = true
            """
            
            cutoff_date = datetime.now() - timedelta(days=540)  # 18 months
            
            result = await conn.fetchrow(
                query,
                normalized_title,
                years_experience,
                location_tier,
                cutoff_date
            )
            
            if not result or result['sample_size'] < 5:
                # Fallback to broader query
                result = await self._fallback_query(
                    conn,
                    normalized_title,
                    location_tier
                )
            
            # Calculate tech stack premium
            tech_premium = self._calculate_tech_stack_premium(tech_stack)
            
            # Adjust for cost of living and tech stack
            market_data = {
                'p10': int(result['p10'] * col_multiplier * tech_premium) if result['p10'] else None,
                'p25': int(result['p25'] * col_multiplier * tech_premium) if result['p25'] else None,
                'p50': int(result['p50'] * col_multiplier * tech_premium) if result['p50'] else None,
                'p75': int(result['p75'] * col_multiplier * tech_premium) if result['p75'] else None,
                'p90': int(result['p90'] * col_multiplier * tech_premium) if result['p90'] else None,
                'sample_size': result['sample_size'],
                'avg_base': int(result['avg_base']) if result['avg_base'] else None,
                'avg_bonus': int(result['avg_bonus']) if result['avg_bonus'] else None,
                'avg_equity': int(result['avg_equity']) if result['avg_equity'] else None,
                'confidence': self._calculate_confidence(result['sample_size']),
                'data_freshness': 'recent' if result['sample_size'] > 0 else 'limited'
            }
            
            return market_data
            
        finally:
            await conn.close()
    
    def _normalize_job_title(self, title: str) -> str:
        """Normalize job title to standard format"""
        title_lower = title.lower()
        
        # Software Engineer variants
        if any(term in title_lower for term in ['software engineer', 'swe', 'software developer']):
            if 'senior' in title_lower or 'sr' in title_lower:
                return 'senior_software_engineer'
            elif 'staff' in title_lower:
                return 'staff_software_engineer'
            elif 'principal' in title_lower:
                return 'principal_software_engineer'
            else:
                return 'software_engineer'
        
        # Other role normalizations...
        return title_lower.replace(' ', '_')
    
    def _get_location_tier(self, location: str) -> str:
        """Categorize location into tiers"""
        tier1_cities = [
            'san francisco', 'sf', 'bay area', 'silicon valley',
            'new york', 'nyc', 'seattle', 'los angeles'
        ]
        
        tier2_cities = [
            'austin', 'boston', 'chicago', 'denver', 'portland'
        ]
        
        location_lower = location.lower()
        
        if any(city in location_lower for city in tier1_cities):
            return 'tier1'
        elif any(city in location_lower for city in tier2_cities):
            return 'tier2'
        else:
            return 'tier3'
    
    def _get_col_multiplier(self, location: str) -> float:
        """Get cost of living multiplier"""
        location_lower = location.lower()
        
        col_multipliers = {
            'san francisco': 1.5,
            'new york': 1.4,
            'seattle': 1.3,
            'boston': 1.25,
            'austin': 1.1,
            'remote': 1.0,
        }
        
        for city, multiplier in col_multipliers.items():
            if city in location_lower:
                return multiplier
        
        return 1.0
    
    def _calculate_tech_stack_premium(self, tech_stack: List[str]) -> float:
        """Calculate premium for in-demand technologies"""
        if not tech_stack:
            return 1.0
        
        premium_tech = {
            'rust': 1.15,
            'golang': 1.10,
            'go': 1.10,
            'kubernetes': 1.12,
            'k8s': 1.12,
            'ai': 1.20,
            'ml': 1.20,
            'machine learning': 1.20,
            'blockchain': 1.15
        }
        
        premiums = []
        for tech in tech_stack:
            tech_lower = tech.lower()
            premium = premium_tech.get(tech_lower, 1.0)
            premiums.append(premium)
        
        if not premiums:
            return 1.0
        
        return sum(premiums) / len(premiums)
    
    def _calculate_confidence(self, sample_size: int) -> str:
        """Calculate confidence level based on sample size"""
        if sample_size >= 100:
            return 'high'
        elif sample_size >= 30:
            return 'medium'
        elif sample_size >= 10:
            return 'low'
        else:
            return 'very_low'
    
    async def _fallback_query(self, conn, normalized_title: str, location_tier: str):
        """Fallback query with broader criteria"""
        query = """
        SELECT 
            percentile_cont(0.25) WITHIN GROUP (ORDER BY total_comp) as p25,
            percentile_cont(0.50) WITHIN GROUP (ORDER BY total_comp) as p50,
            percentile_cont(0.75) WITHIN GROUP (ORDER BY total_comp) as p75,
            percentile_cont(0.90) WITHIN GROUP (ORDER BY total_comp) as p90,
            COUNT(*) as sample_size,
            AVG(base_salary) as avg_base,
            AVG(bonus) as avg_bonus,
            AVG(equity_value) as avg_equity
        FROM salary_data
        WHERE 
            normalized_title = $1
            AND is_verified = true
        """
        
        return await conn.fetchrow(query, normalized_title)
```

## Negotiation Script Generator

```python
# services/script_generator.py
import google.generativeai as genai
import os
from typing import Dict

class NegotiationScriptGenerator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def generate_scripts(
        self,
        analysis_result: Dict,
        user_profile: Dict
    ) -> Dict:
        """Generate personalized negotiation email templates using Gemini"""
        
        offer = analysis_result['offer_data']
        market = analysis_result['market_data']
        verdict = analysis_result['verdict']
        target_salary = analysis_result['negotiation_room']['realistic']
        
        prompt = self._build_prompt(
            offer, market, verdict, target_salary, user_profile
        )
        
        response = self.model.generate_content(prompt)
        scripts_text = response.text
        
        # Parse the three scripts
        scripts = self._parse_scripts(scripts_text)
        
        # Generate additional tips
        tips = await self._generate_negotiation_tips(analysis_result)
        
        return {
            'assertive': scripts.get('assertive', ''),
            'balanced': scripts.get('balanced', ''),
            'humble': scripts.get('humble', ''),
            'tips': tips,
            'talking_points': self._generate_talking_points(analysis_result)
        }
    
    def _build_prompt(
        self,
        offer: Dict,
        market: Dict,
        verdict: str,
        target_salary: int,
        user_profile: Dict
    ) -> str:
        """Build comprehensive prompt for script generation"""
        
        return f"""
Generate 3 professional negotiation email templates for a tech job offer.

**Current Situation:**
- Position: {offer.get('job_title')}
- Company: {offer.get('company')}
- Current offer: ${offer.get('base_salary', 0):,}
- Market median (P50): ${market.get('p50', 0):,}
- Market P75: ${market.get('p75', 0):,}
- Target salary: ${target_salary:,}
- Assessment: {verdict}

**Candidate Background:**
- Years of experience: {user_profile.get('years_experience', 'Not specified')}
- Current/Previous salary: ${user_profile.get('current_salary', 0):,}
- Key skills: {', '.join(user_profile.get('tech_stack', []))}
- Has competing offers: {user_profile.get('has_competing_offers', False)}

Generate 3 distinct email templates with these styles:

**1. ASSERTIVE** (for strong negotiating position)
- Confident tone
- Direct ask
- Higher target number

**2. BALANCED** (for standard negotiation)
- Professional and friendly
- Data-driven justification
- Reasonable ask

**3. HUMBLE** (for weaker position)
- Grateful and enthusiastic
- Gentle ask
- Lower target

Each template must:
- Express genuine enthusiasm
- Present data-driven justification
- Suggest specific number
- Keep door open
- Be 150-250 words

Format: Subject line + Email body

Separate each template with "---TEMPLATE BREAK---"
"""
    
    def _parse_scripts(self, text: str) -> Dict:
        """Parse the three templates from AI response"""
        parts = text.split('---TEMPLATE BREAK---')
        
        scripts = {}
        
        for part in parts:
            part = part.strip()
            if 'ASSERTIVE' in part.upper() or '1.' in part[:50]:
                scripts['assertive'] = self._extract_template(part)
            elif 'BALANCED' in part.upper() or '2.' in part[:50]:
                scripts['balanced'] = self._extract_template(part)
            elif 'HUMBLE' in part.upper() or '3.' in part[:50]:
                scripts['humble'] = self._extract_template(part)
        
        return scripts
    
    def _extract_template(self, text: str) -> str:
        """Extract clean template from text"""
        lines = text.split('\n')
        
        start_idx = 0
        for i, line in enumerate(lines):
            if 'Subject:' in line or 'Hi' in line or 'Dear' in line:
                start_idx = i
                break
        
        return '\n'.join(lines[start_idx:]).strip()
    
    async def _generate_negotiation_tips(self, analysis_result: Dict) -> list:
        """Generate specific negotiation tips"""
        verdict = analysis_result['verdict']
        
        tips = [
            {
                'title': 'Do Your Research',
                'description': 'Reference specific market data for your role.'
            },
            {
                'title': 'Be Specific',
                'description': f"Ask for a specific number (${analysis_result['negotiation_room']['realistic']:,})."
            },
            {
                'title': 'Stay Positive',
                'description': 'Express enthusiasm while negotiating.'
            },
            {
                'title': 'Consider Total Package',
                'description': 'Negotiate bonus, equity, or benefits if base is inflexible.'
            }
        ]
        
        if verdict in ['SIGNIFICANTLY_UNDERPAID', 'UNDERPAID']:
            tips.append({
                'title': 'Leverage Market Data',
                'description': 'The offer is below market rate.'
            })
        
        return tips
    
    def _generate_talking_points(self, analysis_result: Dict) -> list:
        """Generate key talking points"""
        talking_points = []
        
        market_p50 = analysis_result['market_data'].get('p50', 0)
        if market_p50:
            talking_points.append(
                f"Market median is ${market_p50:,}"
            )
        
        for leverage in analysis_result.get('leverage_points', []):
            if leverage.get('strength') in ['strong', 'medium']:
                talking_points.append(leverage['description'])
        
        return talking_points
```

## Salary Database

```python
# services/salary_contribution.py
import asyncpg
import hashlib
from typing import Dict
from datetime import datetime

class SalaryContributionService:
    def __init__(self, db_url: str):
        self.db_url = db_url
    
    async def submit_salary_data(self, data: Dict) -> Dict:
        """Accept anonymous salary contribution"""
        
        # Validate data
        validation = self._validate_submission(data)
        if not validation['is_valid']:
            return {
                'success': False,
                'error': validation['error']
            }
        
        # Verify not duplicate
        submission_hash = self._generate_submission_hash(data)
        
        conn = await asyncpg.connect(self.db_url)
        
        try:
            # Check for recent duplicate
            duplicate = await conn.fetchrow(
                """
                SELECT id FROM salary_data
                WHERE submission_hash = $1
                AND submitted_date > NOW() - INTERVAL '24 hours'
                """,
                submission_hash
            )
            
            if duplicate:
                return {
                    'success': False,
                    'error': 'Duplicate submission detected'
                }
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(data)
            
            # Normalize job title
            normalized_title = self._normalize_title(data['job_title'])
            
            # Get location tier
            location_tier = self._get_location_tier(data['location'])
            
            # Calculate total comp
            total_comp = (
                data.get('base_salary', 0) +
                data.get('bonus', 0) +
                data.get('equity_value', 0)
            )
            
            # Insert into database
            await conn.execute(
                """
                INSERT INTO salary_data (
                    job_title, normalized_title, company, company_tier,
                    location, location_tier, base_salary, bonus,
                    equity_value, total_comp, years_experience,
                    tech_stack, benefits, is_verified,
                    confidence_score, submission_hash, submitted_date
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                """,
                data['job_title'],
                normalized_title,
                data.get('company', 'Anonymous'),
                self._get_company_tier(data.get('company', '')),
                data['location'],
                location_tier,
                data['base_salary'],
                data.get('bonus', 0),
                data.get('equity_value', 0),
                total_comp,
                data['years_experience'],
                data.get('tech_stack', []),
                data.get('benefits', {}),
                confidence >= 0.7,
                confidence,
                submission_hash,
                datetime.now()
            )
            
            return {
                'success': True,
                'message': 'Thank you for your contribution!',
                'confidence_score': confidence
            }
            
        finally:
            await conn.close()
    
    def _validate_submission(self, data: Dict) -> Dict:
        """Validate salary submission data"""
        required = ['job_title', 'location', 'base_salary', 'years_experience']
        for field in required:
            if field not in data or not data[field]:
                return {
                    'is_valid': False,
                    'error': f'Missing required field: {field}'
                }
        
        base_salary = data['base_salary']
        if base_salary < 20000 or base_salary > 1000000:
            return {
                'is_valid': False,
                'error': 'Base salary out of reasonable range'
            }
        
        return {'is_valid': True}
    
    def _calculate_confidence_score(self, data: Dict) -> float:
        """Calculate confidence score for submission"""
        score = 0.0
        checks = 0
        
        if data.get('company'):
            score += 1
            checks += 1
        
        if self._is_reasonable_salary(data['base_salary'], data['years_experience']):
            score += 1
        checks += 1
        
        if data.get('tech_stack') and len(data['tech_stack']) > 0:
            score += 1
            checks += 1
        
        return score / checks if checks > 0 else 0.0
    
    def _is_reasonable_salary(self, salary: int, years_exp: int) -> bool:
        """Check if salary is reasonable"""
        min_salary = 40000 + (years_exp * 10000)
        max_salary = 100000 + (years_exp * 30000)
        
        return min_salary <= salary <= max_salary
    
    def _generate_submission_hash(self, data: Dict) -> str:
        """Generate hash to detect duplicates"""
        hash_string = f"{data['job_title']}|{data['base_salary']}|{data['location']}|{data['years_experience']}"
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def _normalize_title(self, title: str) -> str:
        """Normalize job title"""
        title_lower = title.lower()
        
        if 'software engineer' in title_lower:
            if 'senior' in title_lower:
                return 'senior_software_engineer'
            else:
                return 'software_engineer'
        
        return title_lower.replace(' ', '_')
    
    def _get_location_tier(self, location: str) -> str:
        """Get location tier"""
        tier1 = ['san francisco', 'new york', 'seattle']
        tier2 = ['austin', 'boston', 'chicago']
        
        location_lower = location.lower()
        
        for city in tier1:
            if city in location_lower:
                return 'tier1'
        
        for city in tier2:
            if city in location_lower:
                return 'tier2'
        
        return 'tier3'
    
    def _get_company_tier(self, company: str) -> str:
        """Determine company tier"""
        faang = ['google', 'amazon', 'meta', 'apple', 'netflix', 'microsoft']
        
        if any(f in company.lower() for f in faang):
            return 'FAANG'
        
        return 'Standard'
```

## Database Schema {#database-schema-2}

```sql
-- Salary data table (crowd-sourced)
CREATE TABLE salary_data (
  id SERIAL PRIMARY KEY,
  job_title VARCHAR(200) NOT NULL,
  normalized_title VARCHAR(100) NOT NULL,
  company VARCHAR(200),
  company_tier VARCHAR(20),
  location VARCHAR(100) NOT NULL,
  location_tier VARCHAR(20),
  base_salary INTEGER NOT NULL,
  bonus INTEGER DEFAULT 0,
  equity_value INTEGER DEFAULT 0,
  total_comp INTEGER NOT NULL,
  years_experience INTEGER NOT NULL,
  tech_stack VARCHAR(100)[],
  benefits JSONB,
  is_verified BOOLEAN DEFAULT false,
  confidence_score FLOAT,
  submission_hash VARCHAR(64) UNIQUE,
  submitted_date TIMESTAMP DEFAULT NOW(),
  CONSTRAINT reasonable_salary CHECK (base_salary BETWEEN 20000 AND 1000000)
);

-- User offer analyses
CREATE TABLE offer_analyses (
  id SERIAL PRIMARY KEY,
  user_id UUID,
  session_id VARCHAR(100),
  offer_data JSONB NOT NULL,
  analysis_result JSONB NOT NULL,
  market_data JSONB,
  generated_scripts JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Negotiation outcomes
CREATE TABLE negotiation_outcomes (
  id SERIAL PRIMARY KEY,
  analysis_id INTEGER REFERENCES offer_analyses(id),
  outcome VARCHAR(50),
  final_salary INTEGER,
  increase_amount INTEGER,
  increase_percentage FLOAT,
  user_feedback TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  subscription_tier VARCHAR(20) DEFAULT 'free',
  subscription_expires TIMESTAMP,
  analyses_used INTEGER DEFAULT 0,
  analyses_limit INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_salary_normalized_title ON salary_data(normalized_title);
CREATE INDEX idx_salary_location_tier ON salary_data(location_tier);
CREATE INDEX idx_salary_experience ON salary_data(years_experience);
CREATE INDEX idx_salary_submitted_date ON salary_data(submitted_date DESC);
CREATE INDEX idx_salary_verified ON salary_data(is_verified);

CREATE INDEX idx_salary_query ON salary_data(
  normalized_title,
  location_tier,
  years_experience,
  is_verified,
  submitted_date DESC
);
```

---

## Environment Variables

```bash
# .env.example

# WhatsApp Bot
WHATSAPP_SESSION_PATH=./whatsapp-session

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379

# Code Execution
JUDGE0_API_KEY=your_judge0_api_key

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key

# App Config
NODE_ENV=development
PORT=3000
```

## Package.json (Daily Coding Challenge)

```json
{
  "name": "daily-coding-challenge-whatsapp",
  "version": "1.0.0",
  "description": "Daily coding challenge via WhatsApp",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js"
  },
  "dependencies": {
    "whatsapp-web.js": "^1.23.0",
    "qrcode-terminal": "^0.12.0",
    "pg": "^8.11.0",
    "node-cron": "^3.0.2",
    "axios": "^1.4.0",
    "dotenv": "^16.0.3"
  },
  "devDependencies": {
    "nodemon": "^2.0.22"
  }
}
```

## Requirements.txt (Salary Negotiation Helper)

```txt
fastapi==0.104.1
uvicorn==0.24.0
asyncpg==0.29.0
google-generativeai==0.3.0
PyPDF2==3.0.1
python-multipart==0.0.6
pydantic==2.5.0
python-dotenv==1.0.0
pandas==2.1.3
numpy==1.26.2
```

---

## Deployment Instructions

### Daily Coding Challenge Bot

```bash
# 1. Install dependencies
npm install

# 2. Set up PostgreSQL database
createdb coding_challenge

# 3. Run database migrations
psql coding_challenge < schema.sql

# 4. Set environment variables
cp .env.example .env
# Edit .env with your credentials

# 5. Start bot (will show QR code to scan)
npm start

# Scan QR code with WhatsApp to authenticate
```

### Salary Negotiation Helper

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up database
createdb salary_negotiation
psql salary_negotiation < schema.sql

# 4. Set environment variables
cp .env.example .env
# Add your Gemini API key

# 5. Run FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

*Updated with WhatsApp Web.js and Google Gemini 2.0 Flash*
*Generated on November 10, 2025*
