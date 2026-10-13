"""
Seed script — populates CurriculumDay and VocabularyGroup for all 30 days.
Run:  cd backend && python -m app.seed.seed
"""
import asyncio
import logging
from sqlalchemy import select
from app.database import engine, Base, async_session_factory
from app.models.curriculum import CurriculumDay
from app.models.vocabulary import VocabularyGroup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 30-DAY CURRICULUM
# Week 1 (Days 1-7):  Foundation — Introductions, Self-presentation
# Week 2 (Days 8-14): Thinking in English — Descriptions, Opinions
# Week 3 (Days 15-21): Interview English — Answering, Storytelling
# Week 4 (Days 22-30): Pressure Training — Mock prep, Fluency drills
# Days 7,14,21,28 = milestone mock-interview checkpoints; Day 30 = final
# ═══════════════════════════════════════════════════════════════════════════════

DAYS = [
    # ── WEEK 1: Foundation ──────────────────────────────────────────────────
    {
        "day_number": 1, "week_number": 1, "week_theme": "Foundation",
        "focus_topic": "Introducing Yourself Confidently",
        "grammar_topic": "Subject-Verb Agreement & Simple Present",
        "grammar_lesson_md": "### Subject-Verb Agreement\n- Use **-s/-es** with he/she/it: *She works at Google.*\n- No -s with I/you/we/they: *They work at Google.*\n- Common mistake: ~~He work~~ → **He works**\n\n### Quick Practice\nFill in: I ___ (study) AI. She ___ (develop) models.",
        "speaking_prompt": "Introduce yourself as if you've just met a recruiter at a tech event. Include your name, background, what you study, and one thing you're passionate about in tech.",
        "writing_prompt": "Write a 150-word self-introduction for a job application email. Include your education, key skills, and why you're excited about AI/ML roles.",
    },
    {
        "day_number": 2, "week_number": 1, "week_theme": "Foundation",
        "focus_topic": "Talking About Your Education",
        "grammar_topic": "Past Simple vs Present Perfect",
        "grammar_lesson_md": "### Past Simple vs Present Perfect\n- **Past Simple** = finished action, specific time: *I graduated in 2024.*\n- **Present Perfect** = action connected to now: *I have completed 3 projects.*\n- Tip: Use present perfect for achievements on your resume.\n\n### Common Mistakes\n- ~~I am graduated~~ → **I graduated**\n- ~~I have went~~ → **I have gone**",
        "speaking_prompt": "Describe your educational journey. Where did you study? What subjects interested you most? How did you discover your interest in AI/ML?",
        "writing_prompt": "Write about your most valuable learning experience during college. What did you learn, and how has it prepared you for a technical career? (150 words)",
    },
    {
        "day_number": 3, "week_number": 1, "week_theme": "Foundation",
        "focus_topic": "Describing Your Skills & Strengths",
        "grammar_topic": "Using Can/Could/Be Able To",
        "grammar_lesson_md": "### Ability Expressions\n- **Can** = present ability: *I can write Python scripts.*\n- **Could** = past ability or polite: *I could help with that.*\n- **Be able to** = formal/future: *I will be able to deliver by Friday.*\n\n### Interview Tip\nAvoid: ~~I am having knowledge of~~ → **I have knowledge of** / **I know**",
        "speaking_prompt": "What are your top 3 technical skills? For each, give a brief example of how you've used it in a project.",
        "writing_prompt": "Write a short paragraph describing your strengths as a candidate for a data analyst role. Be specific — use examples, not just adjectives. (150 words)",
    },
    {
        "day_number": 4, "week_number": 1, "week_theme": "Foundation",
        "focus_topic": "Everyday Conversations & Small Talk",
        "grammar_topic": "Question Formation (Wh- & Yes/No)",
        "grammar_lesson_md": "### Question Structures\n- **Yes/No**: Do/Does + subject + verb? *Do you use TensorFlow?*\n- **Wh-**: Wh-word + auxiliary + subject + verb? *What framework do you prefer?*\n- **Common error**: ~~What you are doing?~~ → **What are you doing?**\n\n### Practice\nForm questions: (where / you / work) → Where do you work?",
        "speaking_prompt": "You're waiting for an interview to start and the person next to you is also a candidate. Make small talk — ask about their background, what role they applied for, and share yours.",
        "writing_prompt": "Write a dialogue between two engineering students meeting at a hackathon for the first time. Include at least 5 exchanges. (150 words)",
    },
    {
        "day_number": 5, "week_number": 1, "week_theme": "Foundation",
        "focus_topic": "Numbers, Data & Technical Descriptions",
        "grammar_topic": "Articles (a/an/the) & Quantifiers",
        "grammar_lesson_md": "### Articles\n- **a/an** = first mention, general: *I built a model.*\n- **the** = specific, known: *The model achieved 95% accuracy.*\n- **No article** with uncountable/general: *Machine learning is growing.*\n\n### Common Mistakes\n- ~~I have the good experience~~ → **I have good experience**\n- ~~I trained model~~ → **I trained a model**",
        "speaking_prompt": "Describe a dataset you've worked with. How many rows/features? What patterns did you find? Explain it as if to a non-technical person.",
        "writing_prompt": "Write a brief technical summary of a project or analysis you've done. Include specific numbers — accuracy, dataset size, time taken. (150 words)",
    },
    {
        "day_number": 6, "week_number": 1, "week_theme": "Foundation",
        "focus_topic": "Expressing Opinions & Preferences",
        "grammar_topic": "Comparative & Superlative Forms",
        "grammar_lesson_md": "### Comparatives & Superlatives\n- Short adj: *faster, fastest*\n- Long adj: *more efficient, most efficient*\n- Irregular: *better/best, worse/worst*\n\n### Useful Patterns\n- *Python is easier than Java for data science.*\n- *The most important factor is...*\n- ~~More better~~ → **better**",
        "speaking_prompt": "Compare two technologies you've used (e.g., Python vs R, TensorFlow vs PyTorch). Which do you prefer and why?",
        "writing_prompt": "Write a comparison of two career paths: Data Analyst vs ML Engineer. Discuss pros, cons, and which suits you better. (150 words)",
    },
    {
        "day_number": 7, "week_number": 1, "week_theme": "Foundation",
        "focus_topic": "Week 1 Review & Milestone Interview",
        "grammar_topic": "Review: Tenses, Articles, Questions",
        "grammar_lesson_md": "### Week 1 Grammar Review\nThis week you covered:\n1. Subject-verb agreement\n2. Past simple vs present perfect\n3. Can/could/be able to\n4. Question formation\n5. Articles & quantifiers\n6. Comparatives & superlatives\n\nReview any areas you found difficult before your mock interview.",
        "speaking_prompt": "Practice answering: 'Walk me through your resume' — cover education, skills, projects, and career goals in under 2 minutes.",
        "writing_prompt": "Reflect on your Week 1 progress. What grammar points were new? What's still difficult? What will you focus on next week? (150 words)",
        "is_milestone": True,
    },
    # ── WEEK 2: Thinking in English ─────────────────────────────────────────
    {
        "day_number": 8, "week_number": 2, "week_theme": "Thinking in English",
        "focus_topic": "Describing Processes & Workflows",
        "grammar_topic": "Sequence Words & Passive Voice",
        "grammar_lesson_md": "### Sequence Words\n- *First, I collected the data. Then, I cleaned it. Finally, I trained the model.*\n- Use: first, then, next, after that, finally\n\n### Passive Voice\n- Use when the action matters more than who did it:\n- *The data was preprocessed using pandas.*\n- *The model is trained on 10,000 samples.*",
        "speaking_prompt": "Describe the end-to-end process of a data analysis or ML project you worked on. Walk through each step clearly.",
        "writing_prompt": "Write step-by-step instructions for training a simple ML model, as if explaining to a junior developer. (150 words)",
    },
    {
        "day_number": 9, "week_number": 2, "week_theme": "Thinking in English",
        "focus_topic": "Explaining Concepts Simply",
        "grammar_topic": "Relative Clauses (who/which/that)",
        "grammar_lesson_md": "### Relative Clauses\n- **who** for people: *The engineer who built the API...*\n- **which/that** for things: *The model that we trained...*\n- **Tip**: Keep them short in spoken English.\n\n### Common Errors\n- ~~The person which~~ → **The person who**\n- ~~The model who~~ → **The model that/which**",
        "speaking_prompt": "Explain what machine learning is to someone who has never heard of it. Use an everyday analogy.",
        "writing_prompt": "Write a simple explanation of how a neural network works, using analogies a non-technical person would understand. (150 words)",
    },
    {
        "day_number": 10, "week_number": 2, "week_theme": "Thinking in English",
        "focus_topic": "Giving and Defending Opinions",
        "grammar_topic": "Conditional Sentences (If/Would)",
        "grammar_lesson_md": "### Conditionals\n- **Zero**: *If you clean the data, the model works better.* (general truth)\n- **First**: *If I get this job, I will work hard.* (real future)\n- **Second**: *If I had more time, I would build a better model.* (hypothetical)\n\n### Interview Usage\n- *If given the opportunity, I would contribute to...*",
        "speaking_prompt": "If you could solve any problem with AI, what would it be? Defend your choice with 2-3 reasons.",
        "writing_prompt": "Write your opinion on whether AI will replace data analysts in the next 10 years. Support your argument with reasons. (150 words)",
    },
    {
        "day_number": 11, "week_number": 2, "week_theme": "Thinking in English",
        "focus_topic": "Discussing Problems & Solutions",
        "grammar_topic": "Cause & Effect Language",
        "grammar_lesson_md": "### Cause & Effect Connectors\n- **Because / because of**: *The model failed because the data was noisy.*\n- **Due to / owing to** (formal): *Due to missing values, accuracy dropped.*\n- **As a result / therefore**: *We added more features. As a result, accuracy improved.*\n- **Lead to**: *Overfitting leads to poor generalization.*",
        "speaking_prompt": "Describe a technical problem you faced in a project. What caused it? How did you solve it? What did you learn?",
        "writing_prompt": "Write about a challenge in your college or project life. Explain the problem, your approach to solving it, and the outcome. (150 words)",
    },
    {
        "day_number": 12, "week_number": 2, "week_theme": "Thinking in English",
        "focus_topic": "Presenting Data & Results",
        "grammar_topic": "Reporting Language & Hedging",
        "grammar_lesson_md": "### Reporting & Hedging\n- **Direct**: *The accuracy is 92%.*\n- **Hedging** (softer, more professional):\n  - *The accuracy appears to be around 92%.*\n  - *The results suggest that...*\n  - *It seems that the model performs well on...*\n\n### When to Hedge\n- Preliminary results, uncertain conclusions, or polite suggestions.",
        "speaking_prompt": "Present the results of a project or analysis. Include numbers, what they mean, and what conclusions you drew.",
        "writing_prompt": "Write a mini results section for a project: state the objective, key metrics, and interpretation of results. (150 words)",
    },
    {
        "day_number": 13, "week_number": 2, "week_theme": "Thinking in English",
        "focus_topic": "Agreeing, Disagreeing & Negotiating",
        "grammar_topic": "Modal Verbs for Politeness (should/might/could)",
        "grammar_lesson_md": "### Polite Modals\n- **Should**: *We should consider a different approach.*\n- **Might**: *This might not be the best solution.*\n- **Could**: *Could we try a different algorithm?*\n\n### Agreeing & Disagreeing Phrases\n- Agree: *That's a great point. I agree because...*\n- Disagree: *I see your point, but I think...*\n- Avoid: ~~You are wrong~~ → **I have a different perspective...**",
        "speaking_prompt": "Your teammate suggests using a complex deep learning model for a simple classification task. Politely disagree and suggest a simpler approach.",
        "writing_prompt": "Write an email to your project supervisor politely disagreeing with a technical decision and proposing an alternative. (150 words)",
    },
    {
        "day_number": 14, "week_number": 2, "week_theme": "Thinking in English",
        "focus_topic": "Week 2 Review & Milestone Interview",
        "grammar_topic": "Review: Passives, Conditionals, Hedging",
        "grammar_lesson_md": "### Week 2 Grammar Review\nThis week you covered:\n1. Sequence words & passive voice\n2. Relative clauses\n3. Conditional sentences\n4. Cause & effect language\n5. Hedging & reporting\n6. Polite modal verbs\n\nFocus on using these naturally in your mock interview.",
        "speaking_prompt": "Practice answering: 'Tell me about a challenging project you worked on' using the STAR method (Situation, Task, Action, Result).",
        "writing_prompt": "Write your Week 2 reflection. How has your ability to explain technical concepts improved? (150 words)",
        "is_milestone": True,
    },
    # ── WEEK 3: Interview English ───────────────────────────────────────────
    {
        "day_number": 15, "week_number": 3, "week_theme": "Interview English",
        "focus_topic": "The STAR Method for Behavioral Questions",
        "grammar_topic": "Past Continuous & Past Perfect",
        "grammar_lesson_md": "### Past Continuous\n- Background action: *I was working on the model when the server crashed.*\n\n### Past Perfect\n- Earlier past action: *I had already cleaned the data before I started training.*\n- *By the time I joined the team, they had completed the design.*\n\n### STAR Tip\nUse past perfect for the Situation, past simple for Action & Result.",
        "speaking_prompt": "Answer this interview question using STAR: 'Tell me about a time you had to learn a new technology quickly.'",
        "writing_prompt": "Write a STAR response for: 'Describe a situation where you worked under a tight deadline.' (150 words)",
    },
    {
        "day_number": 16, "week_number": 3, "week_theme": "Interview English",
        "focus_topic": "Strengths, Weaknesses & Self-Awareness",
        "grammar_topic": "Gerunds vs Infinitives",
        "grammar_lesson_md": "### Gerunds (-ing) vs Infinitives (to + verb)\n- After **enjoy, avoid, consider, keep**: use gerund → *I enjoy coding.*\n- After **want, plan, decide, hope**: use infinitive → *I plan to learn Docker.*\n- Both: *I like working / I like to work* (slight difference in register)\n\n### Common Error\n- ~~I am planning to learning~~ → **I am planning to learn**",
        "speaking_prompt": "Answer: 'What are your strengths and weaknesses?' Give one genuine weakness and explain what you're doing to improve it.",
        "writing_prompt": "Write about your biggest professional weakness. How did you discover it, and what steps are you taking to address it? (150 words)",
    },
    {
        "day_number": 17, "week_number": 3, "week_theme": "Interview English",
        "focus_topic": "Why This Role / Why This Company",
        "grammar_topic": "Future Tenses (will/going to/present continuous)",
        "grammar_lesson_md": "### Future Tenses\n- **Will**: spontaneous, promises → *I will give my best.*\n- **Going to**: plans, evidence → *I'm going to apply for the ML team.*\n- **Present continuous**: arranged future → *I'm starting next Monday.*\n\n### Interview Phrase Bank\n- *I'm looking to grow in...*\n- *I plan to contribute by...*\n- *In five years, I see myself...*",
        "speaking_prompt": "Answer: 'Why do you want to work at [company]?' and 'Where do you see yourself in 5 years?' Make them specific, not generic.",
        "writing_prompt": "Write a cover letter paragraph explaining why a specific AI/ML company excites you and what you'd bring to the team. (150 words)",
    },
    {
        "day_number": 18, "week_number": 3, "week_theme": "Interview English",
        "focus_topic": "Technical Explanations in Interviews",
        "grammar_topic": "Defining & Contrasting (whereas/while/unlike)",
        "grammar_lesson_md": "### Contrasting Language\n- **Whereas / While**: *Supervised learning uses labels, whereas unsupervised learning does not.*\n- **Unlike**: *Unlike batch processing, stream processing handles data in real time.*\n- **On the other hand**: *CNNs are great for images. On the other hand, RNNs work better for sequences.*",
        "speaking_prompt": "Explain the difference between supervised and unsupervised learning to an interviewer. Use clear contrasting language.",
        "writing_prompt": "Write a technical comparison between two ML algorithms you know (e.g., Random Forest vs Gradient Boosting). (150 words)",
    },
    {
        "day_number": 19, "week_number": 3, "week_theme": "Interview English",
        "focus_topic": "Handling Tricky Questions",
        "grammar_topic": "Reported Speech & Indirect Questions",
        "grammar_lesson_md": "### Reported Speech\n- Direct: *He said, 'I need the report.'*\n- Reported: *He said that he needed the report.*\n\n### Indirect Questions (more polite)\n- Direct: *What is your salary expectation?*\n- Indirect: *Could you tell me what your salary expectation is?*\n- Note: word order changes! No auxiliary inversion.",
        "speaking_prompt": "Practice answering: 'What are your salary expectations?' and 'Why did you leave your last position?' Handle them diplomatically.",
        "writing_prompt": "Write how you would respond to: 'Tell me about a time you failed at something.' Be honest but frame it positively. (150 words)",
    },
    {
        "day_number": 20, "week_number": 3, "week_theme": "Interview English",
        "focus_topic": "Asking Smart Questions to the Interviewer",
        "grammar_topic": "Question Tags & Clarification Phrases",
        "grammar_lesson_md": "### Question Tags\n- *The team uses agile, doesn't it?*\n- *You mentioned ML pipelines, didn't you?*\n\n### Clarification Phrases\n- *Could you elaborate on that?*\n- *If I understand correctly, you mean...?*\n- *Just to clarify, is the role more focused on...?*\n\n### Smart Question Starters\n- *What does a typical day look like for...?*\n- *How does the team approach...?*",
        "speaking_prompt": "You're at the end of an interview and they ask, 'Do you have any questions?' Prepare and ask 3 thoughtful questions.",
        "writing_prompt": "Write 5 questions you would ask at the end of a Data Analyst interview. Make them specific and insightful, not generic. (150 words)",
    },
    {
        "day_number": 21, "week_number": 3, "week_theme": "Interview English",
        "focus_topic": "Week 3 Review & Milestone Interview",
        "grammar_topic": "Review: STAR, Tenses, Contrasting, Reported Speech",
        "grammar_lesson_md": "### Week 3 Grammar Review\nThis week you covered:\n1. Past continuous & past perfect (for STAR stories)\n2. Gerunds vs infinitives\n3. Future tenses\n4. Contrasting language\n5. Reported speech & indirect questions\n6. Question tags & clarification\n\nYour mock interview today will test all of these in a realistic interview setting.",
        "speaking_prompt": "Full mock interview practice: Be ready for 'Tell me about yourself', a STAR question, a technical question, and 'Do you have questions?'",
        "writing_prompt": "Write your Week 3 reflection. Rate your interview confidence on a 1-10 scale and explain what needs improvement. (150 words)",
        "is_milestone": True,
    },
    # ── WEEK 4: Pressure Training ───────────────────────────────────────────
    {
        "day_number": 22, "week_number": 4, "week_theme": "Pressure Training",
        "focus_topic": "Speed Responses — Thinking on Your Feet",
        "grammar_topic": "Discourse Markers (well, actually, basically)",
        "grammar_lesson_md": "### Discourse Markers for Fluency\n- **Well** — buys time: *Well, that's an interesting question...*\n- **Actually** — corrects/adds info: *Actually, I also worked on NLP.*\n- **Basically** — simplifies: *Basically, we cleaned the data and built a pipeline.*\n- **I mean** — clarifies: *I mean, the main challenge was...*\n\n### Tip: Use these to sound natural, not robotic. Don't overuse!",
        "speaking_prompt": "Quick-fire: Answer these in 30 seconds each — 'What's your biggest achievement?', 'Describe your ideal work environment', 'What motivates you?'",
        "writing_prompt": "Write rapid responses (2-3 sentences each) for 5 common HR questions. Focus on being concise and clear. (150 words)",
    },
    {
        "day_number": 23, "week_number": 4, "week_theme": "Pressure Training",
        "focus_topic": "Group Discussion & Team Communication",
        "grammar_topic": "Linking Ideas (moreover, however, in addition)",
        "grammar_lesson_md": "### Formal Linkers\n- **Adding**: moreover, furthermore, in addition\n- **Contrasting**: however, nevertheless, on the contrary\n- **Concluding**: therefore, consequently, in conclusion\n\n### When to Use\n- Written: Use freely for structure\n- Spoken: Use sparingly — prefer 'also', 'but', 'so' in casual speech\n- Interview: Mix formal and natural for the best impression",
        "speaking_prompt": "Lead a mock group discussion on: 'Should companies replace customer service agents with AI chatbots?' Present multiple viewpoints.",
        "writing_prompt": "Write an argument for and against remote work for tech teams. Use formal linking words to structure your points. (150 words)",
    },
    {
        "day_number": 24, "week_number": 4, "week_theme": "Pressure Training",
        "focus_topic": "Handling Unexpected Topics",
        "grammar_topic": "Mixed Conditionals & Complex Sentences",
        "grammar_lesson_md": "### Mixed Conditionals\n- *If I had studied harder (past), I would be more confident now (present).*\n- *If I were better at SQL (present), I would have gotten that role (past).*\n\n### Building Complex Sentences\n- Combine short sentences: *I learned Python. I used it for data analysis.* → *After learning Python, I used it for data analysis.*\n- Keep them readable — 2 clauses max in spoken English.",
        "speaking_prompt": "Surprise topic: 'Explain how you would use data analytics to improve a local restaurant's business.' Think on your feet — you have no preparation time.",
        "writing_prompt": "Write about a topic you know nothing about (e.g., 'The future of quantum computing in healthcare'). Practice structuring thoughts on unfamiliar subjects. (150 words)",
    },
    {
        "day_number": 25, "week_number": 4, "week_theme": "Pressure Training",
        "focus_topic": "Professional Email & Written Communication",
        "grammar_topic": "Formal vs Informal Register",
        "grammar_lesson_md": "### Register Differences\n| Informal | Formal |\n|----------|--------|\n| I want to | I would like to |\n| Can you | Could you / Would you be able to |\n| Thanks | Thank you for your consideration |\n| FYI | For your information / Please note |\n| ASAP | At your earliest convenience |\n\n### Email Structure\n1. Greeting → 2. Purpose → 3. Details → 4. Action needed → 5. Closing",
        "speaking_prompt": "Role-play: Call a company's HR to follow up on your job application. Be professional and clear about your purpose.",
        "writing_prompt": "Write a professional follow-up email after a job interview. Thank the interviewer, reference something specific from the conversation, and reaffirm your interest. (150 words)",
    },
    {
        "day_number": 26, "week_number": 4, "week_theme": "Pressure Training",
        "focus_topic": "Storytelling & Memorable Answers",
        "grammar_topic": "Narrative Tenses & Vivid Language",
        "grammar_lesson_md": "### Narrative Tenses\n- Set the scene: *I was working on a deadline...* (past continuous)\n- Main events: *I discovered a bug. I fixed it.* (past simple)\n- Background: *I had never seen that error before.* (past perfect)\n\n### Making Answers Memorable\n- Use specific details: not 'a project' but 'a sentiment analysis tool for product reviews'\n- Include emotions: *I was really frustrated, but then I realized...*\n- End with impact: *That saved the team 3 hours per week.*",
        "speaking_prompt": "Tell a story about a 'eureka moment' in a project — when something finally clicked. Make it vivid and engaging.",
        "writing_prompt": "Write a short narrative about overcoming a technical challenge. Use vivid details and narrative tenses to make it compelling. (150 words)",
    },
    {
        "day_number": 27, "week_number": 4, "week_theme": "Pressure Training",
        "focus_topic": "Confidence Building & Positive Self-Talk",
        "grammar_topic": "Emphatic Structures (It is...that / What I...is)",
        "grammar_lesson_md": "### Emphatic Structures\n- **Cleft sentences**: *What I enjoy most is solving complex problems.*\n- **It is...that**: *It was the data cleaning that took the longest.*\n- **Do/Does for emphasis**: *I do believe that AI can transform healthcare.*\n\n### Confidence Language\n- *I am confident that I can...*\n- *I have consistently demonstrated...*\n- *My experience in X has prepared me to...*",
        "speaking_prompt": "Give a 2-minute 'elevator pitch' about yourself as a candidate. Be confident — sell your strengths without being arrogant.",
        "writing_prompt": "Write a LinkedIn summary that showcases your skills, achievements, and career aspirations. Make it professional yet personable. (150 words)",
    },
    {
        "day_number": 28, "week_number": 4, "week_theme": "Pressure Training",
        "focus_topic": "Week 4 Checkpoint & Pressure Mock Interview",
        "grammar_topic": "Review: All grammar topics",
        "grammar_lesson_md": "### Full Grammar Review\nAcross 4 weeks you've covered:\n- Tenses (simple, continuous, perfect, mixed)\n- Articles, quantifiers, comparatives\n- Questions, conditionals, passive voice\n- Relative clauses, reported speech\n- Discourse markers, linking words\n- Formal register, emphatic structures\n\nToday's mock interview will include curveball questions to test your composure.",
        "speaking_prompt": "Pressure mock interview: Be ready for rapid-fire questions, a technical explanation, and one completely unexpected question.",
        "writing_prompt": "Write your Week 4 reflection. Compare your confidence now vs Week 1. What's your biggest improvement? (150 words)",
        "is_milestone": True,
    },
    {
        "day_number": 29, "week_number": 4, "week_theme": "Pressure Training",
        "focus_topic": "Final Preparation & Strategy",
        "grammar_topic": "Common Interview Mistakes to Avoid",
        "grammar_lesson_md": "### Top Grammar Mistakes in Interviews\n1. ~~I am having experience~~ → **I have experience**\n2. ~~I did not knew~~ → **I did not know**\n3. ~~More better~~ → **better**\n4. ~~I have did~~ → **I have done**\n5. ~~Myself John~~ → **My name is John** / **I'm John**\n6. ~~I am belong to~~ → **I belong to** / **I'm from**\n7. ~~He told to me~~ → **He told me**\n\n### Final Tips\n- Speak at a natural pace — not too fast\n- Pause before answering — it shows confidence\n- It's OK to say 'That's a great question, let me think...'",
        "speaking_prompt": "Do a full run-through: self-intro, STAR answer, technical explanation, salary discussion, and closing questions — as if this is the real interview.",
        "writing_prompt": "Write a pre-interview checklist: key points you want to mention, questions to ask, and reminders about body language/speaking pace. (150 words)",
    },
    {
        "day_number": 30, "week_number": 4, "week_theme": "Pressure Training",
        "focus_topic": "Final Interview — Day 1 vs Day 30 Comparison",
        "grammar_topic": "Comprehensive Review",
        "grammar_lesson_md": "### Day 30 — Your Final Interview\n\nThis is your final mock interview. It will be scored and compared against your Day 0 baseline.\n\n**Remember everything you've learned:**\n- Clear introductions\n- STAR method for behavioral questions\n- Simple, natural sentence patterns\n- Confident but honest self-presentation\n- Smart questions for the interviewer\n\nYou've put in the work. Trust your preparation. Good luck!",
        "speaking_prompt": "Final mock interview — full format. This score will be compared to your Day 0 baseline. Give it your best.",
        "writing_prompt": "Final reflection: Write about your journey over 30 days. What changed? What surprised you? What will you keep practicing after this program? (200 words)",
        "is_milestone": True,
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# VOCABULARY GROUPS — 10 per day (abbreviated for days 1-30)
# Each group: headword + related phrases + example sentences
# ═══════════════════════════════════════════════════════════════════════════════

def _v(headword, phrases, examples):
    return {"headword": headword, "phrases": phrases, "example_sentences": examples}

VOCAB_BY_DAY = {
    1: [
        _v("introduce", ["introduce myself", "introduce a concept", "self-introduction"], ["Let me introduce myself — I'm a final-year CS student.", "I'd like to introduce a new approach to this problem."]),
        _v("background", ["technical background", "come from a background in", "background knowledge"], ["I come from a background in computer science.", "My background in math helps me understand ML algorithms."]),
        _v("passionate", ["passionate about", "have a passion for", "pursue my passion"], ["I'm passionate about using AI to solve real-world problems.", "She has a genuine passion for data visualization."]),
        _v("specialize", ["specialize in", "area of specialization", "specialized skills"], ["I specialize in natural language processing.", "My area of specialization is computer vision."]),
        _v("pursue", ["pursue a career", "pursue an opportunity", "pursue further studies"], ["I want to pursue a career in data science.", "I'm pursuing an opportunity to work on cutting-edge ML."]),
        _v("proficient", ["proficient in", "become proficient", "proficiency level"], ["I'm proficient in Python and SQL.", "I became proficient in TensorFlow through self-study."]),
        _v("aspire", ["aspire to become", "aspiring engineer", "career aspirations"], ["I aspire to become a machine learning engineer.", "As an aspiring data scientist, I practice daily."]),
        _v("contribute", ["contribute to a team", "make a contribution", "contribute ideas"], ["I want to contribute to a team building AI solutions.", "I made significant contributions to our capstone project."]),
        _v("develop", ["develop skills", "develop a solution", "professional development"], ["I developed my skills through online courses and projects.", "We developed a solution that reduced processing time by 40%."]),
        _v("experience", ["hands-on experience", "gain experience", "work experience"], ["I have hands-on experience with deep learning frameworks.", "I gained experience through two internships."]),
    ],
    2: [
        _v("graduate", ["graduate from", "recent graduate", "postgraduate"], ["I graduated from XYZ University in 2024.", "As a recent graduate, I'm eager to apply my knowledge."]),
        _v("curriculum", ["curriculum includes", "academic curriculum", "part of the curriculum"], ["Our curriculum included courses in statistics and ML.", "Data structures was a core part of the curriculum."]),
        _v("research", ["conduct research", "research paper", "research interests"], ["I conducted research on sentiment analysis.", "My research interests lie in reinforcement learning."]),
        _v("major", ["major in", "my major is", "major project"], ["I majored in Computer Science with a focus on AI.", "My major project involved building a recommendation system."]),
        _v("semester", ["last semester", "throughout the semester", "semester project"], ["Last semester, I completed an advanced ML course.", "Throughout the semester, I improved my coding skills."]),
        _v("coursework", ["relevant coursework", "complete coursework", "coursework includes"], ["My relevant coursework includes statistics and data mining.", "I completed coursework in both theory and application."]),
        _v("thesis", ["write a thesis", "thesis topic", "defend my thesis"], ["My thesis focused on transfer learning for small datasets.", "I successfully defended my thesis last month."]),
        _v("mentor", ["my mentor", "mentor me in", "mentorship program"], ["My professor mentored me throughout my final year.", "The mentorship program helped me grow professionally."]),
        _v("academic", ["academic performance", "academic background", "academic achievement"], ["My academic performance has been consistently strong.", "I balance academic work with practical projects."]),
        _v("foundation", ["strong foundation", "build a foundation", "foundational knowledge"], ["I have a strong foundation in mathematics.", "The course helped me build a solid foundation in ML."]),
    ],
    3: [
        _v("implement", ["implement a solution", "implementation details", "implement from scratch"], ["I implemented a CNN from scratch using NumPy.", "The implementation took about two weeks to complete."]),
        _v("analyze", ["analyze data", "data analysis", "analytical skills"], ["I analyzed customer data to identify purchase patterns.", "Strong analytical skills are essential for this role."]),
        _v("optimize", ["optimize performance", "optimization techniques", "optimize code"], ["I optimized the model to reduce inference time by 50%.", "We used gradient descent as our optimization technique."]),
        _v("collaborate", ["collaborate with", "team collaboration", "cross-functional collaboration"], ["I collaborated with a team of five engineers.", "Good collaboration is key to project success."]),
        _v("debug", ["debug the code", "debugging skills", "debug an issue"], ["I spent two days debugging a data pipeline issue.", "Debugging skills are crucial for any developer."]),
        _v("deploy", ["deploy a model", "deployment pipeline", "deploy to production"], ["We deployed the model using Docker and Kubernetes.", "The deployment pipeline automates testing and release."]),
        _v("visualize", ["visualize data", "data visualization", "visualization tools"], ["I used Matplotlib to visualize the training metrics.", "Data visualization helps stakeholders understand findings."]),
        _v("automate", ["automate the process", "automation script", "automate testing"], ["I wrote scripts to automate the data cleaning process.", "Automation saved our team several hours per week."]),
        _v("troubleshoot", ["troubleshoot issues", "troubleshooting skills", "troubleshoot errors"], ["I can troubleshoot common ML pipeline failures.", "Troubleshooting skills are developed through practice."]),
        _v("adapt", ["adapt to changes", "adaptable", "adapt quickly"], ["I adapt quickly to new tools and technologies.", "Being adaptable is important in a fast-paced environment."]),
    ],
    4: [
        _v("opportunity", ["great opportunity", "career opportunity", "take the opportunity"], ["This is a great opportunity to grow as an engineer.", "I took the opportunity to learn cloud computing."]),
        _v("appreciate", ["I appreciate", "appreciate the feedback", "greatly appreciate"], ["I appreciate you taking the time to interview me.", "I greatly appreciate any feedback on my work."]),
        _v("suggest", ["I suggest", "suggestion for", "open to suggestions"], ["I suggest we start with exploratory data analysis.", "I'm always open to suggestions from teammates."]),
        _v("prefer", ["I prefer", "preference for", "preferable"], ["I prefer Python for data analysis tasks.", "My preference is for agile development methodologies."]),
        _v("recommend", ["I recommend", "highly recommended", "recommendation"], ["I'd recommend starting with a simple baseline model.", "My professor recommended me for this position."]),
        _v("familiar", ["familiar with", "familiarity", "get familiar with"], ["I'm familiar with scikit-learn and pandas.", "I quickly got familiar with the team's codebase."]),
        _v("curious", ["curious about", "intellectual curiosity", "stay curious"], ["I'm curious about how LLMs handle reasoning tasks.", "Intellectual curiosity drives my learning."]),
        _v("confident", ["confident in", "build confidence", "feel confident"], ["I'm confident in my ability to deliver results.", "Practice has helped me build confidence in interviews."]),
        _v("impressed", ["impressed by", "make an impression", "impressive achievement"], ["I was impressed by the company's AI initiatives.", "Building that app was an impressive achievement."]),
        _v("convenient", ["at your convenience", "convenient time", "user-convenient"], ["Please schedule at your convenience.", "We designed a user-convenient interface."]),
    ],
    5: [
        _v("accuracy", ["model accuracy", "improve accuracy", "accuracy rate"], ["The model achieved 94% accuracy on the test set.", "We improved accuracy by adding more training data."]),
        _v("dataset", ["training dataset", "large dataset", "clean the dataset"], ["We used a dataset of 50,000 labeled images.", "Cleaning the dataset took about 30% of our time."]),
        _v("feature", ["feature engineering", "key features", "extract features"], ["Feature engineering significantly improved model performance.", "We extracted features using PCA."]),
        _v("performance", ["model performance", "high performance", "performance metrics"], ["Model performance improved after hyperparameter tuning.", "We tracked performance metrics across all experiments."]),
        _v("predict", ["predict outcomes", "prediction model", "predictive analytics"], ["The model predicts customer churn with 87% accuracy.", "Predictive analytics helps businesses make better decisions."]),
        _v("significant", ["significant improvement", "statistically significant", "significant impact"], ["We saw a significant improvement in recall.", "The results were statistically significant (p < 0.05)."]),
        _v("approximately", ["approximately 80%", "approximately 1000 samples", "takes approximately"], ["The model processes approximately 100 requests per second.", "Training takes approximately 4 hours on a GPU."]),
        _v("proportion", ["large proportion", "in proportion to", "proportional"], ["A large proportion of the data was unstructured.", "The error rate is proportional to the noise level."]),
        _v("trend", ["upward trend", "identify trends", "market trends"], ["We identified an upward trend in user engagement.", "Analyzing market trends helps predict demand."]),
        _v("exceed", ["exceed expectations", "exceed the target", "exceeded by"], ["Our model exceeded the accuracy target by 5%.", "I aim to exceed expectations in every project."]),
    ],
}

# For days 6-30, generate sensible vocab groups programmatically
_day6_30_vocab_data = {
    6: [
        _v("efficient", ["more efficient", "efficiency gains", "time-efficient"], ["Python is more efficient for prototyping.", "The new pipeline brought major efficiency gains."]),
        _v("compare", ["compare to", "in comparison", "comparable results"], ["Let's compare the results of both models.", "In comparison, the second approach was faster."]),
        _v("advantage", ["key advantage", "take advantage of", "competitive advantage"], ["The key advantage of this method is speed.", "We took advantage of cloud computing resources."]),
        _v("drawback", ["main drawback", "significant drawback", "despite the drawbacks"], ["The main drawback is the long training time.", "Despite the drawbacks, deep learning excels at this."]),
        _v("suitable", ["most suitable", "suitable for", "well-suited"], ["Python is suitable for data science tasks.", "This algorithm is well-suited for small datasets."]),
        _v("alternative", ["viable alternative", "consider alternatives", "alternative approach"], ["We considered several alternative approaches.", "A viable alternative is to use transfer learning."]),
        _v("perspective", ["from my perspective", "different perspectives", "gain perspective"], ["From my perspective, simplicity is key.", "Working in teams gives you different perspectives."]),
        _v("evaluate", ["evaluate performance", "thorough evaluation", "evaluation metrics"], ["We used F1-score to evaluate the model.", "A thorough evaluation is essential before deployment."]),
        _v("flexible", ["flexible approach", "flexibility", "stay flexible"], ["We need a flexible approach to handle edge cases.", "Flexibility is important in agile development."]),
        _v("practical", ["practical experience", "practical application", "practical skills"], ["I gained practical experience through internships.", "This course focuses on practical application of ML."]),
    ],
    7: [
        _v("accomplish", ["accomplish a goal", "key accomplishment", "sense of accomplishment"], ["I accomplished all project milestones on time.", "My key accomplishment was building the data pipeline."]),
        _v("progress", ["make progress", "track progress", "steady progress"], ["I've made significant progress in my communication skills.", "We tracked progress using weekly sprint reviews."]),
        _v("reflect", ["reflect on", "self-reflection", "reflective practice"], ["Let me reflect on what I've learned this week.", "Self-reflection helps identify areas for improvement."]),
        _v("improve", ["improve my skills", "room for improvement", "continuous improvement"], ["I want to improve my public speaking skills.", "There's always room for improvement."]),
        _v("demonstrate", ["demonstrate ability", "demonstration", "clearly demonstrate"], ["I can demonstrate my skills through my portfolio.", "The project clearly demonstrates my problem-solving ability."]),
        _v("prepare", ["prepare for", "well-prepared", "preparation is key"], ["I'm well-prepared for this interview.", "Preparation is key to success in any field."]),
        _v("milestone", ["key milestone", "reach a milestone", "milestone achievement"], ["Completing Week 1 is a key milestone.", "We reached our first milestone ahead of schedule."]),
        _v("consistent", ["consistent effort", "consistently improve", "consistent performance"], ["Consistent effort leads to lasting improvement.", "I consistently improved my test scores."]),
        _v("challenge", ["face challenges", "challenging task", "rise to the challenge"], ["I enjoy facing challenges in my work.", "Building the API was a challenging but rewarding task."]),
        _v("strategy", ["learning strategy", "strategy for improvement", "strategic thinking"], ["My learning strategy includes daily practice.", "Strategic thinking is important for data analysis."]),
    ],
    8: [
        _v("process", ["data processing", "follow a process", "streamline the process"], ["Data processing is the first step in any ML pipeline.", "We streamlined the process using automation."]),
        _v("collect", ["collect data", "data collection", "collect feedback"], ["We collected data from multiple sources.", "Data collection took three weeks."]),
        _v("transform", ["transform data", "data transformation", "transformative impact"], ["We transformed the raw data into features.", "The project had a transformative impact on the team."]),
        _v("validate", ["validate results", "cross-validation", "validation set"], ["We used cross-validation to validate our model.", "The validation set showed consistent accuracy."]),
        _v("pipeline", ["data pipeline", "ML pipeline", "build a pipeline"], ["I built an end-to-end data pipeline.", "The ML pipeline includes preprocessing and training."]),
        _v("iterate", ["iterate on the design", "iterative process", "rapid iteration"], ["We iterated on the model design three times.", "Software development is an iterative process."]),
        _v("execute", ["execute the plan", "execution time", "well-executed"], ["We executed the deployment plan without issues.", "The execution time was under 2 seconds."]),
        _v("sequence", ["in sequence", "sequential steps", "follow a sequence"], ["The steps must be performed in sequence.", "We followed a clear sequence of operations."]),
        _v("integrate", ["integrate with", "system integration", "integrate APIs"], ["We integrated the model with the web application.", "System integration was the final phase."]),
        _v("generate", ["generate reports", "generate predictions", "data generation"], ["The system generates reports automatically.", "We used data augmentation for synthetic data generation."]),
    ],
}

# For remaining days (9-30), create a smaller but valid set
def _generate_remaining_vocab():
    """Generate reasonable vocab groups for days not explicitly defined."""
    topics = {
        9: ("explain", "concept", "simplify", "analogy", "clarify", "illustrate", "comprehend", "interpret", "summarize", "convey"),
        10: ("opinion", "believe", "argument", "justify", "perspective", "viewpoint", "debate", "convince", "assert", "reason"),
        11: ("problem", "solution", "resolve", "identify", "diagnose", "overcome", "approach", "strategy", "tackle", "mitigate"),
        12: ("result", "outcome", "finding", "conclude", "indicate", "reveal", "demonstrate", "evidence", "metric", "benchmark"),
        13: ("agree", "disagree", "negotiate", "compromise", "consensus", "propose", "counter", "acknowledge", "concede", "persuade"),
        14: ("review", "assess", "criterion", "feedback", "iterate", "refine", "enhance", "polish", "finalize", "synthesize"),
        15: ("situation", "task", "action", "outcome", "behavioral", "scenario", "response", "initiative", "leadership", "teamwork"),
        16: ("strength", "weakness", "honest", "genuine", "self-aware", "growth", "resilient", "discipline", "patience", "proactive"),
        17: ("goal", "ambition", "vision", "align", "motivation", "drive", "commitment", "dedication", "aspiration", "milestone"),
        18: ("technical", "algorithm", "framework", "architecture", "scalable", "robust", "efficient", "modular", "abstraction", "paradigm"),
        19: ("diplomacy", "tact", "redirect", "reframe", "composure", "poise", "transparency", "integrity", "discretion", "professionalism"),
        20: ("inquiry", "insight", "culture", "dynamics", "expectation", "scope", "trajectory", "innovation", "impact", "sustainability"),
        21: ("comprehensive", "holistic", "integrate", "synthesize", "cohesive", "articulate", "eloquent", "structured", "methodical", "strategic"),
        22: ("spontaneous", "impromptu", "quick-thinking", "responsive", "instinctive", "decisive", "agile", "resourceful", "alert", "composed"),
        23: ("facilitate", "coordinate", "delegate", "mediate", "participate", "engage", "brainstorm", "consensus", "diverse", "inclusive"),
        24: ("unexpected", "novel", "versatile", "innovative", "creative", "unconventional", "lateral", "inventive", "imaginative", "original"),
        25: ("formal", "professional", "courteous", "concise", "precise", "appropriate", "polished", "respectful", "diplomatic", "eloquent"),
        26: ("narrative", "vivid", "engaging", "compelling", "memorable", "dramatic", "descriptive", "authentic", "relatable", "impactful"),
        27: ("confident", "assertive", "poised", "self-assured", "empowered", "capable", "qualified", "competent", "accomplished", "determined"),
        28: ("pressure", "composure", "resilience", "endurance", "focus", "clarity", "precision", "thoroughness", "consistency", "excellence"),
        29: ("preparation", "rehearse", "anticipate", "contingency", "readiness", "mindset", "visualization", "routine", "ritual", "discipline"),
        30: ("growth", "transformation", "achievement", "journey", "reflection", "gratitude", "progress", "evolution", "confidence", "future"),
    }

    result = {}
    for day, words in topics.items():
        groups = []
        for word in words:
            groups.append(_v(
                word,
                [f"demonstrate {word}", f"show {word}", f"build {word}"],
                [f"I was able to demonstrate {word} throughout the project.",
                 f"This experience helped me build {word} in professional settings."]
            ))
        result[day] = groups
    return result

# Merge all vocab
_remaining = _generate_remaining_vocab()
ALL_VOCAB = {**VOCAB_BY_DAY, **_day6_30_vocab_data, **_remaining}


async def seed_database():
    """Populate CurriculumDay and VocabularyGroup tables."""
    import app.models  # noqa: F401  — ensure all models are registered

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Check if already seeded
        result = await session.execute(select(CurriculumDay).limit(1))
        if result.scalar_one_or_none():
            logger.info("Database already seeded — skipping.")
            return

        logger.info("Seeding curriculum days...")
        for day_data in DAYS:
            is_milestone = day_data.pop("is_milestone", False)
            day = CurriculumDay(
                is_milestone_day=is_milestone,
                **day_data,
            )
            session.add(day)

        await session.flush()

        logger.info("Seeding vocabulary groups...")
        for day_number, groups in ALL_VOCAB.items():
            for g in groups:
                group = VocabularyGroup(
                    day_number=day_number,
                    headword=g["headword"],
                    phrases=g["phrases"],
                    example_sentences=g["example_sentences"],
                )
                session.add(group)

        await session.commit()
        logger.info(f"Seeded {len(DAYS)} curriculum days and vocabulary groups.")


if __name__ == "__main__":
    asyncio.run(seed_database())
