from flask import Flask, request, session, redirect, url_for
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'skillup-secret-2024')

QUESTIONS = [
    {"id":1,"category":"Career Goals","question":"What is your main goal after completing a course?","options":["Get a high-paying job","Switch to a new career","Start my own business","Get a promotion in current job"],"answer":"Get a high-paying job"},
    {"id":2,"category":"Salary Awareness","question":"What is the average starting salary for a Data Analyst fresher in India?","options":["1-2 LPA","3-5 LPA","8-10 LPA","15+ LPA"],"answer":"3-5 LPA"},
    {"id":3,"category":"Salary Awareness","question":"Which skill is most likely to boost your salary the fastest?","options":["MS Word","Data Analysis and Visualization","Basic Computer Knowledge","Typing Speed"],"answer":"Data Analysis and Visualization"},
    {"id":4,"category":"Job Market","question":"Which of these is one of the most in-demand job roles in India right now?","options":["Data Scientist / Analyst","Manual Data Entry","Offline Clerk","Paper Filing"],"answer":"Data Scientist / Analyst"},
    {"id":5,"category":"Skills","question":"Which tool do most companies use to manage and present business data?","options":["Paint","Excel / Power BI","Notepad","Calculator"],"answer":"Excel / Power BI"},
    {"id":6,"category":"Skills","question":"What does a Digital Marketer primarily do?","options":["Deliver products manually","Promote brands online using internet tools","Fix computers","Write code for mobile apps"],"answer":"Promote brands online using internet tools"},
    {"id":7,"category":"Career Goals","question":"What is the best way to get noticed by recruiters on LinkedIn?","options":["Post memes daily","Complete profile with skills, photo and projects","Just create an account and wait","Message 100 people every day"],"answer":"Complete profile with skills, photo and projects"},
    {"id":8,"category":"Salary Awareness","question":"A fresher with Python and Data skills can typically expect a monthly salary of?","options":["5,000-8,000 per month","15,000-20,000 per month","40,000-60,000 per month","1,00,000+ per month"],"answer":"40,000-60,000 per month"},
    {"id":9,"category":"Job Market","question":"Which certificate is most valued by tech employers?","options":["School leaving certificate","Google / Microsoft / AWS certification","Participation in school sports","Typing speed certificate"],"answer":"Google / Microsoft / AWS certification"},
    {"id":10,"category":"Skills","question":"What is ChatGPT and AI tools mainly used for in the workplace?","options":["Playing games","Writing emails, reports and getting coding help","Watching movies","Online shopping"],"answer":"Writing emails, reports and getting coding help"},
    {"id":11,"category":"Job Market","question":"Which sector is hiring the MOST data and tech professionals in 2025?","options":["Agriculture","IT and E-commerce","Transport","Construction"],"answer":"IT and E-commerce"},
    {"id":12,"category":"Salary Awareness","question":"How much more do upskilled candidates earn vs non-upskilled on average?","options":["Same salary","5-10% more","30-50% more","Skills do not affect salary"],"answer":"30-50% more"},
    {"id":13,"category":"Skills","question":"Which of these is a soft skill that every employer looks for?","options":["Python programming","Communication and Teamwork","SQL queries","Cloud computing"],"answer":"Communication and Teamwork"},
    {"id":14,"category":"Career Goals","question":"What is a portfolio in the context of job hunting?","options":["A bag to carry your documents","A collection of your projects and work samples","Your complete salary history","A government ID proof"],"answer":"A collection of your projects and work samples"},
    {"id":15,"category":"Job Market","question":"What is the BEST way to prepare for a job interview?","options":["Memorise everything the night before","Practice mock interviews and research the company","Just hope for the best","Only focus on technical skills"],"answer":"Practice mock interviews and research the company"},
]

CAT_ICON = {"Career Goals":"🎯","Salary Awareness":"💰","Job Market":"📈","Skills":"🛠️"}

def discount(score):
    pct = (score/15)*100
    if pct < 30: return 3, "Keep Going! You are just getting started!"
    elif pct < 50: return 4, "Good Effort! Keep learning and growing!"
    elif pct < 65: return 5, "Nice Work! You have solid career awareness!"
    elif pct < 75: return 7, "Great Job! You know your career path well!"
    elif pct < 90: return 8, "Excellent! You are well prepared for the job market!"
    else: return 10, "Outstanding! You are ready to conquer the job market!"

def save_lead(data):
    leads = []
    if os.path.exists('leads.json'):
        try: leads = json.load(open('leads.json'))
        except: pass
    leads.append(data)
    json.dump(leads, open('leads.json','w'), indent=2)

CSS = """
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0a0f;--surf:#13131a;--card:#1c1c28;--bord:#2a2a3d;--acc:#6c63ff;--gold:#ffd700;--txt:#e8e8f0;--mut:#7a7a9a;--ok:#4ade80;--err:#ff6b6b}
body{background:var(--bg);color:var(--txt);font-family:'DM Sans',sans-serif;min-height:100vh}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 80% 50% at 20% 20%,rgba(108,99,255,.13) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 80% 80%,rgba(255,107,107,.08) 0%,transparent 60%);pointer-events:none;z-index:0}
.wrap{position:relative;z-index:1;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 20px}
.logo{font-family:'Syne',sans-serif;font-weight:800;font-size:18px;background:linear-gradient(135deg,#6c63ff,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:32px}
h1{font-family:'Syne',sans-serif;font-size:clamp(1.8rem,5vw,3.2rem);font-weight:800;line-height:1.15;text-align:center;margin-bottom:14px}
.grad{background:linear-gradient(135deg,#6c63ff,#ff6b6b,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.sub{color:var(--mut);font-size:16px;text-align:center;max-width:480px;line-height:1.7;margin-bottom:36px}
.card{background:var(--card);border:1px solid var(--bord);border-radius:24px;padding:40px 44px;width:100%;max-width:520px;box-shadow:0 40px 80px rgba(0,0,0,.4)}
.card-title{font-family:'Syne',sans-serif;font-size:18px;font-weight:700;margin-bottom:26px}
.fg{margin-bottom:18px}
label{display:block;font-size:12px;font-weight:500;color:var(--mut);margin-bottom:7px;text-transform:uppercase;letter-spacing:.5px}
input,select{width:100%;background:var(--surf);border:1px solid var(--bord);border-radius:12px;padding:13px 15px;color:var(--txt);font-size:15px;outline:none;transition:border-color .2s,box-shadow .2s;font-family:inherit}
input::placeholder{color:#3d3d55}
input:focus,select:focus{border-color:var(--acc);box-shadow:0 0 0 3px rgba(108,99,255,.15)}
select{appearance:none;cursor:pointer;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%237a7a9a' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 15px center}
select option{background:var(--card)}
.btn{width:100%;background:linear-gradient(135deg,#6c63ff,#8b5cf6);border:none;border-radius:14px;padding:15px;color:#fff;font-family:'Syne',sans-serif;font-size:16px;font-weight:700;cursor:pointer;transition:transform .2s,box-shadow .2s;margin-top:6px}
.btn:hover{transform:translateY(-2px);box-shadow:0 12px 32px rgba(108,99,255,.4)}
.err-box{background:rgba(255,107,107,.1);border:1px solid rgba(255,107,107,.3);border-radius:10px;padding:11px 15px;color:var(--err);font-size:14px;margin-bottom:18px}
.chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:36px}
.chip{background:var(--surf);border:1px solid var(--bord);border-radius:50px;padding:6px 14px;font-size:13px;color:var(--mut)}
.dpills{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-bottom:40px}
.pill{background:var(--card);border:1px solid var(--bord);border-radius:14px;padding:12px 20px;text-align:center}
.pill-n{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:var(--gold)}
.pill-l{font-size:11px;color:var(--mut);margin-top:2px}
.badge{display:inline-flex;align-items:center;gap:8px;background:rgba(108,99,255,.12);border:1px solid rgba(108,99,255,.35);border-radius:50px;padding:6px 16px;font-size:13px;color:#a89cff;margin-bottom:22px}
.dot{width:7px;height:7px;background:#6c63ff;border-radius:50%}
.privacy{text-align:center;margin-top:14px;font-size:12px;color:var(--mut)}
.topbar{width:100%;max-width:680px;display:flex;align-items:center;justify-content:space-between;margin-bottom:28px}
.qcount{font-size:14px;color:var(--mut);font-weight:500}
.qcount strong{color:var(--txt);font-family:'Syne',sans-serif}
.prog-wrap{width:100%;max-width:680px;margin-bottom:30px}
.prog-info{display:flex;justify-content:space-between;font-size:12px;color:var(--mut);margin-bottom:7px}
.prog-bar{height:6px;background:var(--bord);border-radius:50px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#6c63ff,#a78bfa);border-radius:50px;transition:width .5s ease}
.cat-tag{display:inline-flex;align-items:center;gap:6px;background:rgba(108,99,255,.1);border:1px solid rgba(108,99,255,.22);border-radius:50px;padding:5px 14px;font-size:12px;color:#a89cff;margin-bottom:18px;text-transform:uppercase;letter-spacing:.7px;font-weight:500}
.qcard{background:var(--card);border:1px solid var(--bord);border-radius:24px;padding:40px 44px;width:100%;max-width:680px;box-shadow:0 30px 60px rgba(0,0,0,.35)}
.qtxt{font-family:'Syne',sans-serif;font-size:clamp(1.05rem,2.5vw,1.35rem);font-weight:700;line-height:1.55;margin-bottom:32px}
.opts{display:flex;flex-direction:column;gap:12px}
.opt{position:relative;background:var(--surf);border:2px solid var(--bord);border-radius:14px;padding:16px 18px 16px 52px;color:var(--txt);font-size:15px;text-align:left;cursor:pointer;transition:border-color .2s,background .2s,transform .15s;width:100%;font-family:inherit}
.opt:hover{border-color:var(--acc);background:rgba(108,99,255,.08);transform:translateX(4px)}
.opt-ltr{position:absolute;left:14px;top:50%;transform:translateY(-50%);width:26px;height:26px;background:var(--bord);border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:'Syne',sans-serif;font-size:12px;font-weight:700;color:var(--mut);transition:background .2s,color .2s}
.opt:hover .opt-ltr{background:var(--acc);color:#fff}
.remind{width:100%;max-width:680px;margin-top:20px;text-align:center;background:rgba(255,215,0,.05);border:1px solid rgba(255,215,0,.13);border-radius:12px;padding:11px 18px;font-size:13px;color:var(--mut)}
.remind strong{color:var(--gold)}
.hero{text-align:center;margin-bottom:36px}
.big-emoji{font-size:60px;display:block;margin-bottom:14px}
.disc-card{background:linear-gradient(135deg,#1a1830,#1c1c28);border:2px solid rgba(255,215,0,.28);border-radius:28px;padding:44px 38px;width:100%;max-width:580px;text-align:center;margin-bottom:28px;box-shadow:0 0 80px rgba(255,215,0,.07),0 40px 80px rgba(0,0,0,.4)}
.disc-lbl{font-size:12px;text-transform:uppercase;letter-spacing:2px;color:var(--gold);margin-bottom:10px;font-weight:500}
.disc-pct{font-family:'Syne',sans-serif;font-size:clamp(5rem,14vw,7.5rem);font-weight:800;color:var(--gold);line-height:1;text-shadow:0 0 60px rgba(255,215,0,.35)}
.disc-off{font-family:'Syne',sans-serif;font-size:19px;color:rgba(255,215,0,.65);margin-bottom:18px}
.disc-msg{font-size:17px;font-weight:600;margin-bottom:22px}
.sco-chips{display:flex;justify-content:center;gap:14px;flex-wrap:wrap}
.sco-chip{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:11px 22px;text-align:center}
.sco-val{font-family:'Syne',sans-serif;font-size:22px;font-weight:800}
.sco-lbl{font-size:11px;color:var(--mut);margin-top:3px;text-transform:uppercase;letter-spacing:.5px}
.coupon{background:var(--card);border:1px dashed rgba(255,215,0,.38);border-radius:16px;padding:18px 26px;display:flex;align-items:center;justify-content:space-between;width:100%;max-width:580px;margin-bottom:28px;gap:14px;flex-wrap:wrap}
.coup-title{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
.coup-code{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:var(--gold);letter-spacing:2px}
.btn-copy{background:rgba(255,215,0,.1);border:1px solid rgba(255,215,0,.3);border-radius:10px;padding:10px 18px;color:var(--gold);font-family:'Syne',sans-serif;font-size:13px;font-weight:600;cursor:pointer;transition:background .2s;white-space:nowrap}
.btn-copy:hover{background:rgba(255,215,0,.2)}
.actions{display:flex;gap:12px;width:100%;max-width:580px;margin-bottom:40px;flex-wrap:wrap}
.btn-pri{flex:1;background:linear-gradient(135deg,#6c63ff,#8b5cf6);border:none;border-radius:14px;padding:15px;color:#fff;font-family:'Syne',sans-serif;font-size:14px;font-weight:700;cursor:pointer;text-decoration:none;display:flex;align-items:center;justify-content:center;gap:7px;transition:transform .2s,box-shadow .2s;min-width:150px}
.btn-pri:hover{transform:translateY(-2px);box-shadow:0 10px 28px rgba(108,99,255,.4)}
.btn-sec{flex:1;background:var(--card);border:1px solid var(--bord);border-radius:14px;padding:15px;color:var(--mut);font-family:'Syne',sans-serif;font-size:14px;font-weight:600;cursor:pointer;text-decoration:none;display:flex;align-items:center;justify-content:center;gap:7px;transition:border-color .2s,color .2s;min-width:150px}
.btn-sec:hover{border-color:var(--acc);color:var(--txt)}
.rev-wrap{width:100%;max-width:680px}
.rev-title{font-family:'Syne',sans-serif;font-size:17px;font-weight:700;margin-bottom:18px}
.rev-item{background:var(--card);border:1px solid var(--bord);border-radius:14px;padding:18px 22px;margin-bottom:10px;border-left:4px solid transparent}
.rev-item.ok{border-left-color:var(--ok)}
.rev-item.bad{border-left-color:var(--err)}
.rev-q{font-size:13px;color:var(--mut);margin-bottom:6px;font-weight:500}
.rev-text{font-size:14px;margin-bottom:9px;line-height:1.5}
.rev-ans{display:flex;flex-wrap:wrap;gap:7px;font-size:13px}
.tag-ok{background:rgba(74,222,128,.1);border:1px solid rgba(74,222,128,.25);border-radius:7px;padding:3px 10px;color:var(--ok)}
.tag-bad{background:rgba(255,107,107,.1);border:1px solid rgba(255,107,107,.25);border-radius:7px;padding:3px 10px;color:var(--err)}
canvas#cf{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:10}
@media(max-width:540px){.card,.qcard,.disc-card{padding:26px 18px}.coupon{flex-direction:column}}
</style>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
"""

@app.route('/')
def index():
    session.clear()
    error = request.args.get('error','')
    err_html = f'<div class="err-box">Warning: {error}</div>' if error else ''
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Career Quiz - Win Fee Discounts!</title>{CSS}</head>
<body><div class="wrap">
  <div class="logo">Career Quiz</div>
  <div class="badge"><div class="dot"></div>FREE Quiz - Win Up To 10% Fee Discount</div>
  <h1>Know Your Career,<br><span class="grad">Earn Your Reward</span></h1>
  <p class="sub">Answer 15 simple questions about jobs, salary and skills - and unlock an exclusive fee discount just for you.</p>
  <div class="chips">
    <div class="chip">🎯 Career Goals</div>
    <div class="chip">💰 Salary Awareness</div>
    <div class="chip">📈 Job Market</div>
    <div class="chip">🛠️ Skills</div>
  </div>
  <div class="dpills">
    <div class="pill"><div class="pill-n">3%</div><div class="pill-l">Starter</div></div>
    <div class="pill"><div class="pill-n">5%</div><div class="pill-l">Good</div></div>
    <div class="pill"><div class="pill-n">7%</div><div class="pill-l">Great</div></div>
    <div class="pill"><div class="pill-n" style="color:#ff6b6b">10%</div><div class="pill-l">Legend</div></div>
  </div>
  <div class="card">
    <div class="card-title">Enter Your Details</div>
    {err_html}
    <form method="POST" action="/register">
      <div class="fg"><label>Full Name *</label><input name="name" type="text" placeholder="Your full name" required></div>
      <div class="fg"><label>Email Address *</label><input name="email" type="email" placeholder="you@gmail.com" required></div>
      <div class="fg"><label>Phone Number *</label><input name="phone" type="tel" placeholder="+91 98765 43210" required></div>
      <div class="fg"><label>College / Institution</label><input name="college" type="text" placeholder="Your college name"></div>
      <div class="fg"><label>Course You are Interested In</label>
        <select name="course_interest">
          <option value="">Select a course...</option>
          <option>Data Science Bootcamp</option>
          <option>Data Analytics Program</option>
          <option>Generative AI Course</option>
          <option>Digital Marketing Mastery</option>
          <option>Full Stack AI + Analytics</option>
        </select>
      </div>
      <button class="btn" type="submit">Start the Quiz</button>
    </form>
    <p class="privacy">Your data is safe. We never share it.</p>
  </div>
</div></body></html>"""


@app.route('/register', methods=['POST'])
def register():
    name  = request.form.get('name','').strip()
    email = request.form.get('email','').strip()
    phone = request.form.get('phone','').strip()
    if not all([name, email, phone]):
        return redirect(url_for('index', error='Please fill in all required fields.'))
    session['user'] = {'name':name,'email':email,'phone':phone,
                       'college':request.form.get('college','').strip(),
                       'course':request.form.get('course_interest','').strip(),
                       'at':datetime.now().isoformat()}
    session['qi'] = 0
    session['ans'] = []
    return redirect(url_for('quiz'))


@app.route('/quiz')
def quiz():
    if 'user' not in session: return redirect(url_for('index'))
    qi = session.get('qi', 0)
    if qi >= len(QUESTIONS): return redirect(url_for('result'))
    q   = QUESTIONS[qi]
    tot = len(QUESTIONS)
    pct = int((qi / tot) * 100)
    icon = CAT_ICON.get(q['category'], '')
    letters = ['A','B','C','D']
    opts_html = ''.join(
        f'<button class="opt" type="submit" name="answer" value="{o}">'
        f'<span class="opt-ltr">{letters[i]}</span>{o}</button>'
        for i, o in enumerate(q['options'])
    )
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Q{qi+1}/{tot} - Career Quiz</title>{CSS}</head>
<body><div class="wrap" style="justify-content:flex-start;padding-top:32px">
  <div class="topbar">
    <div class="logo" style="margin-bottom:0">Career Quiz</div>
    <div class="qcount">Question <strong>{qi+1}</strong> of <strong>{tot}</strong></div>
  </div>
  <div class="prog-wrap">
    <div class="prog-info"><span>Your Progress</span><span>{pct}% complete</span></div>
    <div class="prog-bar"><div class="prog-fill" style="width:{pct}%"></div></div>
  </div>
  <div class="cat-tag">{icon} {q['category']}</div>
  <div class="qcard">
    <div class="qtxt">{q['question']}</div>
    <form method="POST" action="/answer"><div class="opts">{opts_html}</div></form>
  </div>
  <div class="remind">Every correct answer gets you closer to <strong>10% off</strong> your course fee!</div>
</div>
<script>
  document.querySelectorAll('.opt').forEach(b=>b.addEventListener('click',function(){{
    document.querySelectorAll('.opt').forEach(x=>{{x.style.pointerEvents='none';x.style.opacity='0.5'}});
    this.style.opacity='1';this.style.borderColor='#6c63ff';this.style.background='rgba(108,99,255,.15)';
  }}));
</script></body></html>"""


@app.route('/answer', methods=['POST'])
def answer():
    if 'user' not in session: return redirect(url_for('index'))
    qi  = session.get('qi', 0)
    sel = request.form.get('answer','')
    if qi < len(QUESTIONS):
        ans = session.get('ans', [])
        ans.append({'qi':qi,'sel':sel,'correct':QUESTIONS[qi]['answer'],'ok':sel==QUESTIONS[qi]['answer']})
        session['ans'] = ans
        session['qi']  = qi + 1
    return redirect(url_for('quiz'))


@app.route('/result')
def result():
    if 'user' not in session: return redirect(url_for('index'))
    answers = session.get('ans', [])
    score   = sum(1 for a in answers if a['ok'])
    disc, msg = discount(score)
    user  = session['user']
    acc   = int((score/len(QUESTIONS))*100)
    wrong = len(QUESTIONS) - score
    tail  = user['phone'][-4:] if len(user['phone']) >= 4 else '0000'
    code  = f"CAREER{disc}OFF{tail}"
    emoji = '🏆' if disc==10 else ('🚀' if disc>=7 else ('⭐' if disc>=5 else '🌱'))
    first = user['name'].split()[0]

    save_lead({**user,'score':score,'total':len(QUESTIONS),'discount':disc,'done':datetime.now().isoformat()})

    rev_rows = ''
    for a in answers:
        q   = QUESTIONS[a['qi']]
        cls = 'ok' if a['ok'] else 'bad'
        if a['ok']:
            ans_html = f'<span class="tag-ok">Correct: {a["sel"]}</span>'
        else:
            ans_html = f'<span class="tag-bad">Your answer: {a["sel"]}</span><span class="tag-ok">Correct: {a["correct"]}</span>'
        rev_rows += f"""<div class="rev-item {cls}">
          <div class="rev-q">Q{a['qi']+1} &middot; {q['category']}</div>
          <div class="rev-text">{q['question']}</div>
          <div class="rev-ans">{ans_html}</div>
        </div>"""

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Your Results - Career Quiz</title>{CSS}</head>
<body>
<canvas id="cf"></canvas>
<div class="wrap" style="justify-content:flex-start;padding-top:40px">
  <div class="logo">Career Quiz</div>
  <div class="hero">
    <span class="big-emoji">{emoji}</span>
    <h1>Congratulations,<br><span class="grad">{first}!</span></h1>
    <p class="sub" style="margin-bottom:0">{msg}<br>You scored <strong>{score} out of {len(QUESTIONS)}</strong> and earned a special discount!</p>
  </div>
  <div class="disc-card">
    <div class="disc-lbl">Your Exclusive Fee Discount</div>
    <div class="disc-pct">{disc}%</div>
    <div class="disc-off">OFF Your Course Fee</div>
    <div class="disc-msg">{msg}</div>
    <div class="sco-chips">
      <div class="sco-chip"><div class="sco-val" style="color:#4ade80">{score}</div><div class="sco-lbl">Correct</div></div>
      <div class="sco-chip"><div class="sco-val" style="color:#ff6b6b">{wrong}</div><div class="sco-lbl">Wrong</div></div>
      <div class="sco-chip"><div class="sco-val" style="color:#a78bfa">{acc}%</div><div class="sco-lbl">Accuracy</div></div>
    </div>
  </div>
  <div class="coupon">
    <div><div class="coup-title">Your Discount Code</div><div class="coup-code" id="cc">{code}</div></div>
    <button class="btn-copy" onclick="copy()" id="cb">Copy Code</button>
  </div>
  <div class="actions">
    <a href="tel:+918438741522" class="btn-pri">Call to Claim Discount</a>
  </div>
  <div class="rev-wrap">
    <div class="rev-title">Your Answer Review</div>
    {rev_rows}
  </div>
</div>
<script>
function copy(){{
  navigator.clipboard.writeText(document.getElementById('cc').textContent);
  const b=document.getElementById('cb');
  b.textContent='Copied!';b.style.color='#4ade80';
  setTimeout(()=>{{b.textContent='Copy Code';b.style.color=''}},2000);
}}
(function(){{
  const c=document.getElementById('cf'),ctx=c.getContext('2d');
  c.width=innerWidth;c.height=innerHeight;
  const cols=['#6c63ff','#ffd700','#ff6b6b','#4ade80','#a78bfa'];
  const ps=Array.from({{length:100}},()=>({{x:Math.random()*c.width,y:Math.random()*c.height-c.height,w:Math.random()*9+4,h:Math.random()*5+2,col:cols[Math.floor(Math.random()*cols.length)],spd:Math.random()*3+1,ang:Math.random()*6.28,spin:(Math.random()-.5)*.2}}));
  let f=0;
  function draw(){{
    ctx.clearRect(0,0,c.width,c.height);
    ps.forEach((p,i)=>{{p.y+=p.spd;p.x+=Math.sin(f*.02+i)*.8;p.ang+=p.spin;
      ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.ang);
      ctx.globalAlpha=Math.max(0,1-(p.y/c.height)*.9);
      ctx.fillStyle=p.col;ctx.fillRect(-p.w/2,-p.h/2,p.w,p.h);ctx.restore();
    }});
    f++;if(f<220)requestAnimationFrame(draw);else ctx.clearRect(0,0,c.width,c.height);
  }}
  setTimeout(draw,100);
}})();
</script>
</body></html>"""


@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("Starting Career Quiz at http://localhost:5000")
    app.run(debug=True, port=5000)
