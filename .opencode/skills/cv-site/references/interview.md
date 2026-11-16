# The interview

Three rounds, four questions maximum each. The whole point is that the
user talks for a few minutes and then has a site. Everything you can read
from the CV, read it; questions are for decisions and for what the CV
cannot contain.

Ask in the user's language. Use the `question` tool when the answer is a
choice; use plain prose when they need to write something longer.

---

## Round 1 — facts and exposure

Start by reading the CV, then post a compact table:

```
Name        Ada Lovelace
Headline    Software engineer · analytical engines
Location    London, UK
Now         Senior engineer, Analytical Engines Ltd (2023 — )
Before      Engineer, Babbage & Co (2020 — 2023)
Education   BSc Mathematics, University of London (2016 — 2019)
Links       github.com/ada · linkedin.com/in/ada · ada@example.com
```

> "This is what I read from your CV. Correct anything that is wrong or
> out of date."

Then, in the same round:

1. **What should a stranger remember after 30 seconds?**
   Default: current role, the project you are proudest of, what you want
   next. If they say "everything", pick three and ask them to confirm the
   pick.
2. **Which contact details may be public?**
   Multi-select: email / GitHub / LinkedIn / personal site / location
   (city). Phone and home address are never offered; if the CV has a
   phone, mention once that you are leaving it out.
3. **Is there a photo you want on it?**
   Default: no photo, name only. Ask them to put a square JPG or PNG next
   to the folder you will use and give you the path.
4. **Anything in the CV that is confidential?**
   Client names under NDA, unreleased products, internal metrics. If yes,
   ask what to generalise to ("a payments client", "a large retailer").

Stop there. Do not ask about tone yet.

## Round 2 — the shape of the page

Show the menu as a multi-select, with the defaults already selected:

| Section | Default | Ask for |
| --- | --- | --- |
| About | ✅ | 2–4 sentences in their voice |
| Experience | ✅ | already in the CV |
| Projects | ✅ | 2–4 items, one line each + link |
| Contact | ✅ | nothing |
| Writing / talks | ☐ | 3–6 items with links, only if they exist |
| Education | ☐ | keep if early career or academic |
| Skills | ☐ | a short list, never a wall of badges |
| Now | ☐ | one paragraph on what they are doing this month |

Then at most three follow-ups **in total**, for the sections they added.
The usual ones:

- "For each project: what is it, and what makes it yours?" — you write
  the copy from this, you do not ask them to write it.
- "Do you want to link the code, the live demo, or neither?" — default:
  whatever exists; never invent a URL.
- "How do you want to be contacted, and how fast do you answer?" — turns
  into one honest line in Contact.

If they choose Writing or Talks, insist on links and check them. A list
of five posts with two dead links is worse than three working ones.

## Round 3 — style and destination

1. **Language:** English / Spanish / both.
   Ask this last, because "both" only matters once there is content.
   Explaining: "Both adds a toggle in the top bar and doubles the text."
2. **Look:** `ide` (dark bar, monospace labels, light body) or `paper`
   (all light, serif). One sentence each; they can change it later by
   editing one word.
3. **Where does it live?** — `<username>.github.io` if they want the
   root domain, otherwise a project repo named after the site. Explain
   the URL difference in one line, not the mechanics.
4. **Publish now or hand over the folder?**
   If they want to publish: "Is `gh` installed? Run `gh auth status`."
   Their answer decides whether you use `publish.py` or print the manual
   steps.

---

## Handling the awkward answers

- **"Just make it look good."** Pick the defaults, say what you picked in
  one line, and move on. Do not re-ask.
- **"I don't know what to write about myself."** Ask for a story instead:
  "What did you fix last month that someone thanked you for?" Then write
  the paragraph from their answer and show it for correction.
- **"Can you make me sound senior?"** Refuse gently: "I'll keep the
  wording plain and let the work sound senior." Then use the strongest
  concrete facts they gave you.
- **"Add that I'm an expert in X."** Ask for the evidence. If there is
  none, put X in a sentence with what they actually did.
- **Long rambling answer.** Take the facts, write the section, show it.
  Editing a draft is easier for them than answering more questions.
- **No CV at all.** Interview-only: name, current work, three things they
  did, one project, contact. That is enough for a first version.
- **Non-technical CV.** Same structure: experience timeline, selected
  work as cards, writing/talks if any. Drop Skills unless it is a real
  requirement in their field.

## The final check, before publishing

Say this out loud, once:

> "Everything on the page now comes from your CV or from your answers.
> Read the three sections once more — if any sentence would be awkward to
> defend in an interview, tell me and I'll cut it."

That is the last question. Then build, verify, screenshot, publish.
