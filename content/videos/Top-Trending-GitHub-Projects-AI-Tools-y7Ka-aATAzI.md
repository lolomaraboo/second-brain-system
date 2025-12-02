---
title: "Top Trending GitHub Projects - AI Tools"
video_id: y7Ka-aATAzI
date: 2025-12-01
url: https://www.youtube.com/watch?v=y7Ka-aATAzI
tags: [ai, github, opensource, tools]
---

Hey creators, welcome to top trending
and open- source GitHub projects. This
week, part two, where you'll discover
powerful new tools on GitHub that can
instantly level up your workflow. Today,
we explore tools like Farra 7B, an AI
that automates real computer tasks and
Revo Grid, a lightning fast data grid
for web apps. Let's dive in and see what
you can build with these gems.
>> Welcome back to Manu AGI tutorials. Here
we explore the exciting world of AI,
latest AI tools for you. So don't forget
to hit that subscribe button and the
notification bell so you don't miss out
on the latest AI insights. So let's
start today's video.
>> Project number one, LLM Council. Many
LLM debate yields one consensus answer.
Imagine asking a tough question, not to
one AI model, but to a whole council of
them, each with its own style,
strengths, and weaknesses, and then
getting back a well-rounded answer
shaped by consensus. That's exactly what
LLM Council does. It's an open-source
local web app that uses the service Open
Router to broadcast your prompt to
multiple large language models, LLMs,
collects their independent responses,
lets them anonymously review and rank
each other, and finally hands everything
to a designated chairman model that
synthesizes a final answer. When you
submit a query, here's how it works.
First, each council member LLM answers
separately. Then in the review stage,
each sees the other models answers
without knowing who wrote which and
ranks them by accuracy and insight.
Finally, the chairman takes all
responses, critiques, and rankings and
crafts one consolidated output. This
matters now because it moves beyond just
a single LLM. You get diverse
perspectives, peerreview style vetting,
and a consensus that can reduce
hallucinations or bias from a single
model. For people building tools, doing
research or working on complex prompts,
LLM Council offers more robust answer
generation and safer reasoning. It runs
locally backend in Python with fast API
plus async HTTPX front end in React and
stores conversation logs as JSON files.
Give it a try and see how multiple minds
rather than just one reshape the way you
get answers.
>> Before we move to next project, let me
introduce you to TZA app. TZA is your
smart all-in-one productivity companion.
Organizing your life, simplifying your
workflow, and helping you achieve more
with ease. Welcome to effortless
productivity. Let's take another quick
look at these features. Starting with
Sora 2. Just open the Sora 2 interface,
drop your prompt into the box, hit
generate, and wait a few seconds. Your
result will be ready instantly. Let's
take a look. Strength in every detail.
Precision in every move.
Valor time refined.
>> Now moving on to the shortcut clips
feature. Open the tool. Paste your URL
or upload a file. Then select your clip
configuration. Choose your style. Hit
export. And in moments your finished
clip is ready. Let's check out the
results.
>> Million is luxury island. $45 million is
Vishal Island. 5 million.
Next is the amazing texttory feature.
Open the texttory tool and enter your
conversation or idea.
[Music]
Click generate script with AI. Then
choose your personal details theme and
any other options.
After that, pick your background audio
and hit export. In a few seconds, your
story will be fully processed and ready.
Let's enjoy the final result.
>> Dude, you won't believe what just
happened at work.
>> Let me guess, Karen finally got fired.
>> Worse, remember how Mr. Thompson's been
acting weird?
>> Yeah, mumbling to himself and hiding in
the supply closet. What about it?
>> He brought a live chicken to the
meeting. Go explore the tool. Have fun
with the features. So why are you
waiting? Try Teesa app link in the
description and let's move on to our
next project.
>> Project number two, code mode. Execute
code to call any tool in one shot.
Imagine telling an AI agent instead of
use tool A then B then C to just write a
small script that does the job. That's
exactly what code mode offers. a
plug-and-play library under the umbrella
of universal tool calling protocol or
UTCP that lets agents call many
different tools by executing a single
block of code rather than juggling
dozens of separate tool calls. Code mode
wraps up all the complexity. You import
the client, register your tools, APIs,
CLIs, etc. Then ask the agent to run a
small script in Typescript or Python
that calls those tools as needed. The
agent writes the code. The library
executes it inside a sandbox with
timeouts, security isolation, and full
logging. This lets developers and AI
tool builders work more efficiently.
Instead of exposing hundreds of tools
directly to the model, which often leads
to confusing function call overload, you
expose just one, the code exeutor. That
reduces overhead, speeds up workflows,
in some cases 60 to 90% fewer operations
than traditional tool chaining, and
keeps everything secure and manageable.
It's ideal for advanced AI agents,
orchestration systems, automation
pipelines, anywhere you need flexible,
reliable tool integration without the
usual complexity. Try it and watch how
your tool calling workflow becomes
cleaner and smarter. Project number
three, ADK Go code first toolkit for
building AI agents in Go. Imagine
building an AI assistant the same way
you write a cloud backend. Clean,
modular, and fully in your control.
That's what agent development kit ADK
for Go delivers. A free open-source
toolkit from Google that lets you build,
orchestrate, evaluate, and deploy
sophisticated AI agents using Go. ADK Go
treats agents like first class building
blocks. You define agents, autonomous
units using native Go idioms. Agents can
use language models via LLM agents for
reasoning or act as deterministic
workflow controllers. Sequential
parallel or loop agents for predictable
tasks, tools, APIs, code execution,
external services can be wired in and
agents can call them or even delegate
work to other agents because it's code
first. your logic orchestration and tool
integration live as ordinary Go code,
giving you type safety, concurrency
support, easy versioning, and the
ability to run agents alongside your
existing Go services. ADK is model
agnostic and deployment agnostic. Though
optimized for Google's models, you can
plug in different LLM backends, then
deploy locally in containers or on cloud
services like Cloud Run or Google
managed runtimes, making it practical
for real world production use. For
developers, back-end teams or AI tool
builders who prefer Go over Python orJS,
ADK Go offers a robust, scalable path to
integrate AI agents directly into
applications. Try it and see how
smoothly your backend becomes
intelligenceaware. Project number four,
memory. CQL native memory layer for AI
agents. Imagine a world where your AI
assistant doesn't forget past
conversations, where it remembers your
preferences, past tasks, and context
across sessions just like a human would.
That's what memory brings to the table.
This open-source memory engine by Gibson
AI plugs into any LLM or agent framework
with a single line of code,
memory.enable, enable and gives your AI
persistent queryable memory. Memory
stores all memory in standard SQL
databases, SQLite, posgress, MySQL that
you control. That means no blackbox
vector stores, no vendor lockin, and in
full transparency and portability. You
can export or backup memory like any
other database. Under the hood, memory
uses structured entity extraction,
relationship mapping, and full text CQL
search to store facts, user preferences,
context, skills, rules, and more. You
can opt for short-term working memory
for immediate context, long-term memory
for persistent information, or a mix of
both, letting the system intelligently
promote what matters over time. because
it hooks into most popular LLM
frameworks and agent systems like
OpenAI, Anthropic, Light LLM, or
frameworks built on top of them. Memory
works as a universal memory layer for
developers, researchers, or anyone
building contextual personalized AI
assistants. If you want your AI agents
to remember, adapt, and grow smarter
over time, integrate memory and see how
context and continuity make your agent
experiences feel human. Project number
five, Cogn. Smart memory layer for AI
agents. Imagine giving your AI assistant
a brain. Not just short-term memory, but
a growing self-organizing memory that
remembers conversations, documents,
images, and more, and lets the agent
recall them later. That's what Cognet
offers. Cogn is an open-source
Python-based memory engine that helps
you build a persistent knowledge graph
and vector store for your AI agents with
just a few lines of code. Instead of
relying on simple retrieval augmented
generation rag with raw text chunks,
Cogn extracts structured entities,
relations, and semantic connections from
your data from PDFs, transcripts, docs,
images, and stores them in a graph plus
vector database. This lets an AI agent
search not only by keywords but by
meaning, context and relationships,
people, dates, events, concepts, giving
far richer and more accurate memory
recall. You install Cogn via pip feed in
your data, run its Cogn pipeline,
classification, chunking, graph
creation, and then you can ask queries
like what did we decide about project X
last month or show me all documents
about topic Y even if the data was given
weeks ago. Cogn is built for developers,
researchers, and teams building
long-term AI assistance, knowledgebased
tools, or document-driven workflows.
With it, AI systems gain memory, context
awareness, and continuity, reducing
hallucinations and boosting reliability.
Give it a try and see how your agents
memory turns from fleeting to
dependable. Project number six, Zappy,
automatic API discovery tool for AI
agents. And imagine having a tool that
watches a web app use itself, clicking
buttons, filling forms, browsing pages,
and quietly logs every hidden API call
behind the scenes, then turns those raw
calls into structured, readytouse tools
for AI agents. That's exactly what Zappy
does. It's an open-source MIT licensed
Python library from Adopt Aai that
automates API discovery by running
browser sessions via Playright,
capturing network traffic, filtering it
to extract only API relevant calls and
exporting them as HR logs or tool
definitions. Zipa supports converting
discovered APIs into agent-friendly
tools for frameworks like Langchain,
complete with type-S safe schemas and
optional custom headers. So agents can
call endpoints directly as functions
instead of guessing URLs or crafting
HTTP calls manually. It also takes care
of credential handling. You can provide
keys for external LLMs or services like
OpenAI, Anthropic, Google, Grock and
Zappy handles encryption, AES 256GCM and
secure loading before tests or
execution. Zappy matters now because as
apps grow and change, keeping API
definitions in sync manually becomes
errorprone and timeconuming for
developers, AI tool builders and teams
building agentic workflows where AI
agents need to call backend APIs
reliably. Zappy turns a brittle manual
process into an automated reproducible
one. It gives full control, visibility,
and speeds up building realworld AI
integrations. Give it a try and see how
effortlessly your app's hidden APIs
become part of an intelligent automated
agent workflow. Project number seven,
Uptime Kit Terminal and web-based uptime
monitor for your services. Imagine
having a simple self-hosted tool that
quietly watches all your websites, APIs,
or servers every minute and tells you
immediately if something goes down.
That's exactly what Uptimekit delivers.
It's a free MIT licensed open- source
uptime monitoring solution you can run
locally or on your server. Uptime Kit
supports multiple monitor types, HTTPS,
DNS, Incip, Ping, so it works whether
you're tracking a website, a DNS record,
or a bare server. It offers a real-time
dashboard web UI with response time
charts, status history, and colored
status indicators. Green for
operational, yellow for degraded, red
for down, so you get clear visibility of
system health. You can deploy it easily
via Docker, frontend plus backend to
SQLite, making setup quick and painless,
even if you just have a small server or
VPS. For developers, CIS admins, site
owners, or hobbyists running web
services. This gives you full control,
no vendor lockin, and peace of mind.
Your downtime alerts and logs stay with
you. Try it today and see how effortless
monitoring your stack can become.
Project number eight, agent SOP.
Standard procedure workflows for AI
agents. Imagine you could describe a
complex multi-step workflow like review
this PR, update docs, run tests, deploy
in plain markdown, and then hand that to
an AI agent and have it follow exactly
those steps reliably and repeatably.
That's exactly what Agent SOP delivers.
It's an open-source project under Apache
2.0 know that defines a standardized
markdownbased format for AI agent
workflows called SOPs, standard
operating procedures, yet keeps
everything in natural language. When you
write an SOP, you define parameters, a
clear overview/objective,
and step-by-step instructions using RFC
2119 keywords like must, should, may to
give the agent structured constraints
and guidance. These SOPs can then be
used across different agent frameworks
or LLM. The approach gives you the
reliability of scripted workflows with
the flexibility and reasoning power of
LLMs. This matters today because many AI
agents built purely by let the model
decide everything often produce
unpredictable or inconsistent results in
real world tasks. Agent SOP offers a
middle ground. Workflows that stay human
readable, reusable, and sharable yet
enforce structure so agents behave
consistently. developers, AI tool
builders, researchers, or teams
deploying automation pipelines benefit
most. You get clarity, control,
repeatability, and easier collaboration
across agents or teams. Try writing an
SOP for a repeatable task, and let your
agent do the work. It might turn your
chaotic workflows into smooth
automation. Project number nine,
blueprint MCP, autogenerate architecture
diagrams from code bases. Here's
something that feels like the future.
Imagine dumping your project's source
code into a tool and getting back a
clear professional architecture diagram
showing modules, data paths, function
flows, or API interactions without you
drawing a single arrow. That's what
Blueprint MCP does. It's an open- source
Python tool by Arcade AI that connects
with their wider MCP ecosystem and uses
external engines to analyze code and
output full diagrams that visualize your
system structure. With Blueprint MCP,
you start by installing their CLI and
logging into the Arcade platform. Then
you trigger diagram generation via
methods like start diagram job. And once
done, you can download diagram,
resulting in a PNG or base 64 encoded
image that maps out modules and
interactions in your project. This can
turn tens of thousands of lines of
legacy or complex code into an easy to
understand flowchart or architecture
map, saving hours of code reviews or
onboarding effort. The tool works
handinhand with other Arcade MCP
servers. Meaning you can also visualize
API flows, authentication paths, or
cross-service data pipelines if your
project uses cloud services like Google
Drive, GitHub, or others supported by
Arcade. Blueprint MCP matters because
many projects accumulate complexity fast
and humans alone find it hard to track
every interaction, dependency, and
module. With automated diagram
generation, architects, dev leads, or
even solo developers get clarity and
documentation instantly. Give it a try
and see how your code's hidden structure
turns into an instant sharable
blueprint. Project number 10, agent
sandbox skill. Safe, flexible sandbox
environment for AI agent coding and
experiments. Imagine giving an AI agent
full power to write, build, test, or
even host code, but inside a cage, so it
can't harm your real system. That's what
agent sandbox skill does. It provides
isolated sandbox environments via E2B
sandboxes. So agents like cloud code,
Gemini CLI or other CLI based agents can
safely run commands, build full stack
apps, install packages or run browser
automation, all without risking your
host machine. Agent Sandbox skill
supports full stack development
workflows. Agents can scaffold front-end
back-end projects, for example, using
Vue plus fast API skolite, run build and
test cycles, even perform browser
automation using built-in integration
with tools like Playright. It manages
sandbox life cycles, isolating file
systems and network access per agent
fork, so you can spin up as many
independent agent sessions as you like,
each with its own safe environment. The
tool is aimed at developers, AI tool
builders, or teams who want to delegate
real engineering tasks to AI agents, yet
keep full control, safety, and
reproducibility. With this setup, you
can use agents to prototype code, test
ideas, build many apps without worrying
about accidental file corruption, or
unwanted network access. Give it a try
and see how your AI powered coding
experiments stay safe, clean, and
scalable. Thanks for watching. If you
like this roundup, please hit like,
subscribe to the channel, comment which
repo you loved most, and enable
notifications so you don't miss next
video. Don't forget to start the repos
and try out the demos linked in the
description. And if you know more cool
projects I should cover next time, drop
them in the comments below.