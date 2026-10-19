# Use A-GPS in Claude, ChatGPT, Gemini or Grok

No coding. No setup. About 2 minutes.

## Step 1 · Open this link and copy everything

### 👉 [ OPEN THE PROMPT ](https://raw.githubusercontent.com/christianwagar/agps/main/integrations/any-llm/agps-prompt.txt)

A page of plain text opens. Select all (**Ctrl+A**, or **⌘+A** on Mac), then copy (**Ctrl+C** / **⌘+C**).

## Step 2 · Paste it into a new chat

Open a **new chat** in Claude, ChatGPT, Gemini or Grok. Paste (**Ctrl+V** / **⌘+V**) and press Enter.

## Step 3 · Attach your spreadsheet when it asks

The AI will say hi and ask for your accounts. Attach or paste your spreadsheet. Any columns and any column names work. It figures them out, tells you what's missing (that's fine), asks up to 3 optional questions (type **skip** to use the defaults), and gives you:

- Every account with a score and a group, **P1** (best growth bets) to **P4**
- A one-line "why" for each account
- Your top 3 to focus on this week

Then ask it anything, like "explain Acme" or "why is this one P4?"

---

## Quick questions

**No spreadsheet yet?** Type `sample` when it asks, or download the [sample spreadsheet](https://raw.githubusercontent.com/christianwagar/agps/main/examples/sample_accounts.csv) and attach it. You can also just type a few accounts in your own words.

**Is my data private?** That depends on the AI tool you use. With real customer data, use the AI tool your company approves.

**Numbers look off?** Tell it in plain English: "our biggest customers are $200K, not $1M", "marketing matters more for us", or "Acme should be higher, here's why." It'll adjust and rescore.

**Why tune it at all?** A-GPS is a framework, not a magic number. The defaults were set for one book of business. Your customer spend, deal sizes and risk appetite are different, so adjust it until the P1s look like accounts your team would actually bet on.

**Hundreds of accounts?** Big files can be too much for one chat. Split the file into chunks, or have a developer use the [Python package](../../README.md#quickstart).
