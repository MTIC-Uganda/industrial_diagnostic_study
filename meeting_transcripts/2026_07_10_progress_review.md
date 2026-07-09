# MIDD Catch-up, 2026-07-10

**Date:** 2026-07-10
**Attendees:** Hillary Arinda, Jerome Nuwabaasa, Solomon Ariho
**Topics:** MIDD progress + UTIMBER

---

## Summary

A MIDD progress review that turned strategic, with a substantial UTIMBER planning segment at the end. Three headlines:

1. **MIDD has ministerial pull.** The senior minister and the Minister for Trade want a mapping of all industries, with the collected data flowing live into the auto-synthesizing platform MIDD already built. A major validation and expansion of the concept.
2. **The pipeline is nearly done.** Solomon expects to finish it around tomorrow; everything now reads from PocketBase. Dashboard cleanup and the Ask MIDD assistant come after the pipeline is locked.
3. **UTIMBER is now contracted and time-bound.** The July deliverable is the system specification documents (user journey, data exchange protocol, product description), reviewed and taken to a government walkthrough around 23 July. Stack confirmed as Java and Flutter.

---

## MIDD

### Strategic / new
- Commissioner is in Arusha, back about 15 July. Jerome wants the platform issues cleared before then.
- The senior minister and the Minister for Trade are interested in the data and have asked for a **mapping of all industries**. As the mapping is done, the data should feed automatically into the platform that synthesizes it live, which is exactly what MIDD built.
- The mapping is a detailed field exercise: the same firm used for the earlier census work visits each of the 7,011 industries with enumerators, capturing GPS and detailed information (products, exact location, current status). Some of the 7,011 no longer exist; many lack GPS today, so the map cannot yet plot all of them.
- MTIC will likely be asked to design the data collection tool. This is a new inbound source for the same pipeline.

### Architecture decision (Hillary)
- Because we can control how field data arrives (a structured form), the **AI cleaning layer can be dropped for that pipeline**. The AI layer only exists to structure unstructured uploads (between step 1 upload and step 2 extract); structured input needs no cleaning, which also removes the risk of AI misinterpretation.
- The data collection tool should be a **module of the existing app, built as a Progressive Web App**, not a separate native mobile app. It loads cleanly on a phone. Budget it as its own module but keep it tightly coupled to the main app.
- The orchestrator (Python, with AI access) handles the new field source into staging, then promote to production: the same pattern as the current pipeline.

### Pipeline status
- Solomon and his agent are actively using the pipeline and closing holes one at a time. Solomon: not worse, close to done, possibly finished tomorrow.
- **Key friction:** Solomon's agent waits blind because it does not receive the WhatsApp notifications. Fix agreed: the agent already has full backend access (like Hillary's), so it should **monitor the logs and infrastructure directly** rather than wait. This should speed it up significantly.
- Confirmed win: all dashboard data now comes from PocketBase.

### Dashboard cleanup (after the pipeline is locked)
- Card / breakdown names not displaying: they vanished during the color change, not a database issue. Restore them.
- Region map: one color per region, subdivided by shade (darker for higher counts, like a population heatmap; Kampala darker than the rest). Do the same for sectors (e.g. beverages subdivided the way districts are).
- Contrast: white on yellow is unreadable; move label text to black; scale darkest to lightest by value.
- Legend: icons only. Put the district count next to the district name in the detail panel, plus a single aggregated total on top, not in the legend.
- Overlapping labels need cleaning. The map should focus on products stage to stage (inputs); detail lives in the Value Chain Explorer.

### Ask MIDD (the assistant)
- Generating real excitement with the Commissioner: people want to ask a question directly (e.g. how many industries in Masaka and of what kind) rather than navigate.
- It works but improves with real usage. Plan to have **Dennis stress-test it** (he is good at breaking things); give him a test suite.
- Staging Ask MIDD is deliberately more capable than the public one and can run PocketBase queries directly. Future: light pre-training on how to answer specific questions, a per-device compounding memory that learns from usage, and a navigation-assistant role. All after the pipeline.

### Jerome's parallel work: metadata (defendable sources)
- For every card and indicator, document how the figure is calculated (the formula) and the source file for the data (e.g. manufacturing value added: what it is, the formula, the UBOS report it comes from).
- Jerome is building this as an Excel, then will bundle the files and send them to Solomon to upload, so the system can explain each figure: this value is calculated using this formula and this source file. Ties directly to ADR-021.

---

## MIDD action points

### Solomon
- Finish the pipeline (target about tomorrow); it is your project, own any blockers.
- Instruct your agent to **monitor the backend logs and infrastructure directly** (it has full access) instead of waiting on notifications it cannot see.
- Reach out directly when blocked; do not wait for the check-in.
- After the pipeline: dashboard cleanup (restore card names; one-color-per-region shaded map; black labels and contrast; icons-only legend; count next to district name plus an aggregated total; subdivide sectors).
- Take Jerome's metadata files (when sent) and upload them so each figure carries its formula and source.

### Hillary
- Get Solomon's agent onto backend monitoring; keep closing pipeline holes as they surface.
- Once the ministers formalize the mapping ask, design the field data collection tool as a **PWA module** of the existing app (new orchestrated source; no AI cleaning needed for structured input).
- Line up Dennis to stress-test Ask MIDD with a test suite.

### Jerome
- Finish the per-indicator metadata (formula plus source per card) and send the files to Solomon to upload.
- Formalize the ministers' mapping request and the data collection tool ask.

---

## UTIMBER (for the dedicated UTIMBER session)

### Decisions / context
- Contracts are out. July is now delivery-based: agree what is delivered in July, who does what, and surface approval bottlenecks early. Payment is monthly against agreed deliverables plus timesheets.
- **July major deliverable: the system specification documents.** Jerome confirmed "system specification document" = "system design document" (same thing).
- Three documents: **user journey** (Jerome sent an improved, tabulated version, same columns as the draw.io), **data exchange protocol**, **product description**. All are drafts needing review, not sealed.
- **Stack confirmed: switched from Python + React to Java + Flutter.** Locked; changing again would be very costly. Rationale (defense in depth) is in the ADRs.
- Process: start from the user journey (defines end to end what must happen), then the data exchange protocol (entities to integrate with, what data is exchanged, how structured, what to collect at each stage). Jerome takes these to a recorded government walkthrough (tentatively Thursday 23 July, possibly 24th) for buy-in, then filters feedback back to Hillary. No build design before approvals.
- **Biggest open item: who does what (role allocation).** Needs the user journey resolved first.
- Provision early: Apple developer membership ($99/year per person, about 3 days to approve) for iOS; start AWS discussions early.
- Hillary's proposed sequence after the specs: wireframes / look and feel (screens, fonts, transitions) agreed and stamped before front-end coding; backend starts in parallel with mocked integrations (e.g. MTN), giving a scaffolded MVP within about a week.
- Payment model: paid on effort (hours times rate), reconciled to days for reporting. Team rates about $50 to $60+ per hour. Rough estimate for the system docs: about 40 hours each, 4 people, about $60/hour, roughly $10k; earlier ballpark for the wider scope was 50 to 60k. Hillary to compute combined man-hours and split per person.

### UTIMBER next points (Hillary)
- Go through the **user journey** Jerome sent (tonight and tomorrow) and answer Jerome's questions. This is the immediate unblock.
- Feed the user journey into the **system design document**.
- Resolve **who does what** (role allocation) off the user journey.
- Communicate the July plan and responsibilities to the team (James, Andrew, Justine); compute combined hours and the per-person split for the ~$10k system-docs deliverable.
- Keep the team's architecture / ADR work moving (tech and security choices with rationale); Java + Flutter locked.
- Prepare for the **23 July government walkthrough** (user journey plus data exchange protocol are the artifacts Jerome presents).
- Deliverable window: **two weeks** for the system specification documents; squeeze earlier if possible.

---

## Raw transcript

<!-- Paste the raw transcript below this line. Once pasted, I'll produce the
     write-up + summary + action points above, and distribute per the routine
     (Jerome = action bullets, Solomon = detail, TASKS.md). -->

     Jerome Nuwabaasa
You know it's like I saw late like you like it's still day at your place.
Hillary Arinda
No this living setting.
Jerome Nuwabaasa
that's a
Hillary Arinda
belt
Jerome Nuwabaasa
That's one hero about man.
Hillary Arinda
Eh, I think it's a reflection.
Jerome Nuwabaasa
Yeah, how are you?
Hillary Arinda
good How you guys?
Jerome Nuwabaasa
I'm okay.
Hillary Arinda
okay
Jerome Nuwabaasa
Yeah, you sound that bit low is yes.
Hillary Arinda
Hey, wait is the volume low so go in the go? and now
Jerome Nuwabaasa
Now it's better.
Hillary Arinda
Hi, I'm transcribing this call with my Tactiq AI Extension. https://tactiq.io/r/transcribing
Okay, no, it's because I'm not suited. Let me see it properly. okay
Jerome Nuwabaasa
okay and Solomon can you lead us in a Prayer and we begin? Thank you.
Solomon Ariho
Loving father, I won't thank you for the gift of life on. Thank you for the gift of friends and family and thank you for the gift of wisdom and knowledge non-thank you for the projects that you've given to us having father one. Thank you for every bit that we've managed to achieve and everything else. We are going to do loving father invite you to his meeting lead us at everything we discuss be. For the greater good.
Of us our families and our country at large bless us bless our families and everything we do be successful and believe.
Jerome Nuwabaasa
amen okay so Maybe let's start from I've been I've been seeing okay. Let me start with just a few updates. Just a few general updates. Hillary I don't know if you've sent through your acceptance yet. Okay, I don't check that email A lot has problems. That emtek email. it has problems but okay that's good and okay okay I sent some things through on jit. okay okay I hope what I said.
Hillary Arinda
And then I meant. Yes, you also in copy of the male.
Jerome Nuwabaasa
make sense
Hillary Arinda
Yeah, I think in gyms has I got confirmation from gyms. I'm now waiting for cover measurement from the American But yeah everyone was excited. Thank you. That's what I've been reviewing now just that Andrew had sent something before so he was on high in the priority list but after Andrews which I have sorted
Jerome Nuwabaasa
but because I invested a lot of time in it if it doesn't make sense then I'll
Hillary Arinda
I'll be going on to use they had to. yeah We shall know. The difference that no it should make sense.
Jerome Nuwabaasa
I hope I hope it does I I didn't work in the draw IO but I use that format and I tabulated.
Hillary Arinda
Okay, but the end result is the same right.
Jerome Nuwabaasa
It's the same it's a it's a it's exactly what would have been in the dry or but
Hillary Arinda
That's what matters yeah.
Jerome Nuwabaasa
in a table.
Hillary Arinda
Okay wow, that's good.
Jerome Nuwabaasa
Yeah, same columns the columns that were in the dry or the same ones that that
Hillary Arinda
okay good
Jerome Nuwabaasa
in that yeah. now What's the other thing? yes, I maybe this now first because the other update I want to give is the commissioner travel to Arusha And by the time he comes back which will be some type mid next week. I think 15.

🎯
Decision
Really, I hope we would have taken care of most of the issues on this platform. Actually, my hope is that would be done with whatever we need to do with it for now because we will have to do much more with this because we we had a meeting both the senior minister Sanjay and they have the Minister for trade interested. I told you they are interested in data, but now the resisted that we have to do in mapping of all Industries And basically we agreed that as we do the mapping.
The data should be automatically be going into some kind of platform that is automatically seen a sizing it. Which is something that I believe we've already built.
Hillary Arinda
hmm
Jerome Nuwabaasa
It's it's what we are trying to perfect but we've basically built it what it means is let me share my screen just to give contacts. What it means is as the data comes in this figures keep changing?
Hillary Arinda
Dynamically very good.
Jerome Nuwabaasa
They just keep changing whatever we would have done here. So there's this because where we we are getting this is this then there is There is here. where You see here. We talk about gap upset. This is because we don't have data. Maybe the music let me pick something that is for. and and still
Hillary Arinda
And it's rich.
Jerome Nuwabaasa
yeah But it will change also so you see still slab-ups and no flat casting in Uganda USD flat imports let's say. he everything is upset in Uganda
Hillary Arinda
Well, that's a bag.
Jerome Nuwabaasa
That's funny to pick iron, so some of these things are here. So once we put it then this changes you get this changes you you but it's essential is that this
Hillary Arinda
yeah
Jerome Nuwabaasa
data comes in and then the system just keeps synthesizing automatically I mean at the end of the day you have a platform that is tearing telling the story from the data that has come in rather than going to the field you collect data okay for about. Four five months and after collecting the data then now you sit down to start analyzing the data, so that's why normally you find that by the time someone produces a report from the data that they collected. That report is so old.
Hillary Arinda
scale yeah
Jerome Nuwabaasa
I don't know if you've ever observed this is usually the problem you a report comes out and then when you look at the data the data is for AI go. And the gap is no we had first collect the data then take time to analyze it into a report then produce the report then maybe publish the report so by the time you read the report this is an analysis based on data. That is a year old and this.
A kind of sets you back, so this we need to have in place will continuously improve it even as we are working on the on the whatever has working what the
Hillary Arinda
another project
Jerome Nuwabaasa
data and other project as we are collecting the data, but at least we have the Beginning point.
Hillary Arinda
So I have a question.
Jerome Nuwabaasa
yeah
Hillary Arinda
Are you going? Are you saying we are going to collect data again?
Jerome Nuwabaasa
so let me Let me clarify this bit. I need to come here, so you see we have these seven thousand eleven Industries So we are going to visit each one of them. Where it's not as higher enumerators, who will visit them. And they'll get details about each one of them now. Some of these seven thousand
Solomon Ariho
oh
Hillary Arinda
hmm
Jerome Nuwabaasa
eleven Industries some of them no longer exist.
Hillary Arinda
okay
Jerome Nuwabaasa
This is as of the last time corrected. So this is not exactly very accurate data then you see here we have unspecified. It's like we know the industry we have the name but we are not very sure way it is. So all these will be addressed that this every industry will be clear where it is. They will be a GPS they will be some detailed information about the industry, what kind of products does it produce and all of that.
Hillary Arinda
Oh let sorry cut your should so in the other map view you can see this 63.
Jerome Nuwabaasa
No, you can't no in the map view you can't even see the seven thousand eleven
Hillary Arinda
okay
Jerome Nuwabaasa
because not all of them have GPS we know the district where it is, but we do not know the exact location.
Hillary Arinda
Got you, so they are consistency yeah, yeah.
Jerome Nuwabaasa
yeah So we are basically getting more detailed data. This is an analysis of the data based on what we have but we are getting more deeper detail details of the data. Okay, so that's that's the entire. That's what we are doing.
Hillary Arinda
So question sorry, I'm getting ahead of myself the platform these enumerate as they have their own platform. What's the deal?
Jerome Nuwabaasa
so the plan is to hire the same Farm we want to hire the same firm that that we hired for this exposive Research Institute one higher the same form so to do the that kind of It's not really a sense as but it's more like a detailed mapping.
Hillary Arinda
mmm
Jerome Nuwabaasa
so Essentially s would basically be asking us because we have the it aspect of the organization. Obviously asking us to design the tool for correction, so we can design that tool in such a way that the data comes directly.
Hillary Arinda
That's that's good news. yeah
Jerome Nuwabaasa
We got we it does it depends really? but
Hillary Arinda
Because what I was thinking here if we have control of how the data comes in then. We may have to remove the AI layer. Totally unjust loading to pocket spending on yeah, yes.
Jerome Nuwabaasa
okay
Hillary Arinda
That makes it a lot easier and it removes Edge like funny education that polarize because of AI misinterpreting information and stuff. That would be the easier way to do it.
Jerome Nuwabaasa
okay In in the current pipeline, what is the AI layer?
Hillary Arinda
The ailayer is the one that gets the data fast and brexit into where I should go cleans it you get do you remember the picture I shared on the group yes, yes if
Jerome Nuwabaasa
Yes, yes, I remember.
Hillary Arinda
you could just go to it quickly it will paint a better story than my blubbery. Just click on that images or something. I've seen a lot of stuff.
Jerome Nuwabaasa
this this is what is
Hillary Arinda
hey That one yes now. There is another one first. Let me see.
Jerome Nuwabaasa
this the one
Hillary Arinda
One that has numbers okay next just keep clicking next to the picture will load.
Jerome Nuwabaasa
Is it older or newer?
Hillary Arinda
Hey, wait, you don't have ah no. No, I didn't send it to you. You're in my in the group
Jerome Nuwabaasa
which group
Hillary Arinda
The yeah, this is the one.
Jerome Nuwabaasa
Oh, no, I'm not in the group this this is. Yeah, but this is the group this is the one.
Hillary Arinda
But yeah, I think in the group. Yes.
Jerome Nuwabaasa
okay
Hillary Arinda
And this is the AI one continue. To another picture, this is still the AI in the way.
Jerome Nuwabaasa
And then if it's older. It can't be that old.
Hillary Arinda
Go back again. Pocket base see where the one where you supported base the one way go back in front okay, this one will work. Let's use this one as maximize it. okay so You see number one upload full from Jerome client this was the original we know this is Solomon really so zero upload plus full intent right now. We go to staging staging uploader follow the your following the staging upload the number
Jerome Nuwabaasa
Yes, yes.
Hillary Arinda
two llm reads and extracts now is the AI Yes clot. Cli brain Plus orchestrator number three is seed now seeding is basically loading data into a database. That's where so your question is between number one and number two as the answer.
Jerome Nuwabaasa
okay okay and
Hillary Arinda
So number four if you can continue now that we have a chance to go through number four. We go to the staging dashboard where you first see before you take to production. You first see what it looks like the number five where is number five? Know how God I'm not ready? Number five number five review This Is Now You reviewing this does this look
Jerome Nuwabaasa
review
Hillary Arinda
normal number and now asko correct when it doesn't make sense you're like sable. This is staging ask my DD mm-hmm the number six applied to production scroll down or click on hide this theme of stop sharing. But it's click on yeah aha now 16 you apply to production promote the Script no
Jerome Nuwabaasa
Oh, yeah.
Hillary Arinda
name is involved right then. Copy approved data rebuild you get so the staging pocket base at this point when you promote is now in sync with the production pocket base. That is where the production the production UI reads from.
Jerome Nuwabaasa
So the la LM is only at staging.
Hillary Arinda
Yes, that's where you need it because everything else is is very deterministic. You don't need an llm.
Jerome Nuwabaasa
Yes, okay okay.
Hillary Arinda
Yes.
Jerome Nuwabaasa
This is good. I this is okay. I don't so for you saying that if you are collecting data. We can structure the
Hillary Arinda
We skip the the you see the whole point of the upload that is to structure the data into some things structurable data comes in whatever format and then we
Jerome Nuwabaasa
hmm
Hillary Arinda
clean it with AI now if you can control how the data comes in you don't need to
Jerome Nuwabaasa
Yes.
Hillary Arinda
clean it. You can count you can.
Jerome Nuwabaasa
Yeah, but this is this is only one set of data, but these other ones will still keep coming in.
Hillary Arinda
yes for the oh, so what I'm saying is for where data is coming in in form of a form that one we we automatically take it to the staging DB
Jerome Nuwabaasa
Hillary Arinda
And then promote it production.
Jerome Nuwabaasa
okay
Hillary Arinda
Yeah that that's that so we can have another pipeline but always being orchestrated like you see the orchestrator is really Python but python has access to AI so that still can control another source of data, which is a mobile application in the field. So everything is being handled by the orchestrator but Trent Dales
Jerome Nuwabaasa
okay okay
Hillary Arinda
Yeah, that's that's what that propose.
Jerome Nuwabaasa
So, that's it. We we have a tool that we've designed once it's been approved. We can then design it into what what do they call those those tools that you used for data, but they online ones. Solomon
Hillary Arinda
you know
Jerome Nuwabaasa
What do they call that?
Hillary Arinda
form applications or data collection tools
Jerome Nuwabaasa
Yeah, there's a guy who the thing that your friend Chris special.
Solomon Ariho
I record I recorded by the name.
Jerome Nuwabaasa
so, Hillary
Hillary Arinda
hmm
Jerome Nuwabaasa
Sort of one has a friend. You and you you being friendly sometimes costs you.
Solomon Ariho
I no no no. No I now have only two stop saying I have. Through our way all that garbage.
Jerome Nuwabaasa
So some of one has a friend.
Solomon Ariho
had maybe had
Hillary Arinda
a different past tense
Jerome Nuwabaasa
All decrease with whom they started a company and when Chris did a few jobs. He started doing those jobs outside the company and basic really should say did necess anyway, but this is what is really an
Hillary Arinda
That's my new.
Jerome Nuwabaasa
Is what? This is what is what for unfortunately.
Solomon Ariho
I'd look I don't introduce you to fools so the unreference of money. You know mama guess.
Jerome Nuwabaasa
Now Hillary this is the this is a thing that Chris specialized in one thing and
Hillary Arinda
hey
Jerome Nuwabaasa
one thing only.
Hillary Arinda
hmm
Jerome Nuwabaasa
When you'd be going to the field to collect data. You'd have a tool. Then he would digitize this tool. I remember the last one he being for us was. Solomon that thing we use to collect data about about forestry what what? Was the name but it would really be like a Google form? Where you just go online you have a tab and you just keep selecting it so that as you could select it goes into some central database and it's basically what we are talking about now. Now this is one of the simplest things for AI to do.
and Chris Chris on the hazard clients who have not yet discovered AI
Hillary Arinda
That's the one day job. So one hour one hour because I have templates that I already exists.
Jerome Nuwabaasa
It's not a baby. It's not even a day joke. yeah
Hillary Arinda
That is what it does.
Solomon Ariho
United Is it among the products the other foot things?
Hillary Arinda
hmm It must be there but that one is so simple. I don't think we have it. We have only Siri as tools tonakida today pose.
Jerome Nuwabaasa
Hey, what do you mean what what are those things?
Solomon Ariho
Wrinkle has what has for the applications ready for customers.
Hillary Arinda
wrinkle
Jerome Nuwabaasa
I'm telling you.
Hillary Arinda
What we are building A Wrinkle the world the world is not ready.
Solomon Ariho
Very high possible when you when you come when you come saying you see I went
Jerome Nuwabaasa
hey
Solomon Ariho
through this problem and we have an up for it.
Jerome Nuwabaasa
yeah
Hillary Arinda
And you're going.
Jerome Nuwabaasa
Yeah, so I think I think that's that that's what was that. Yes, so that's the general generally the plan this.
Hillary Arinda
That's laying out the plan and I've understood the plan it's a it's a clean
Jerome Nuwabaasa
Yeah, so the issue. Is that we need this ready?

✅
Action Item
Hillary Arinda
plan.
Jerome Nuwabaasa
We really need to get this ready. I'm going to really try my best put in extra time for this.
Hillary Arinda
Actually, we don't need to make an application like we don't need a mobile mobile app. We can make it a module of this application just for that. yeah, but e
Jerome Nuwabaasa
But can it be accessible it up?
Hillary Arinda
H is then this accessible network.
Jerome Nuwabaasa
Checked it.
Hillary Arinda
You should try. It's just not the most not so smooth, because it is very long
Jerome Nuwabaasa
okay
Hillary Arinda
things so it wouldn't make sense for a tabby, but it loads on the phone cleanly
Jerome Nuwabaasa
hmm
Hillary Arinda
and since it's too graphical of course it doesn't make so much sense on a phone. But my point is this one works very well. I would say for a data collection tool you should you would be wasting time to develop a mobile fast application you just develop a progressive web application remember the stuff. I used to tell you back then. I don't know if you remember but yes, yes something that feels
Jerome Nuwabaasa
Yes, yes, I remember remember.
Hillary Arinda
and actually acts like a native application, but it's a web app now web
Jerome Nuwabaasa
Yes.
Hillary Arinda
application have advanced so if it's not if you're not going to do very sophisticated more mobile intensive things. Be wasting resources, just be building.
Jerome Nuwabaasa
I
Hillary Arinda
Maybe for budget issues. We can make it a separate mod of its own such that it's budgeted for different but it should be. Tightly coupled to this.
Jerome Nuwabaasa
okay okay, so
Hillary Arinda
yeah
Jerome Nuwabaasa
A few things that I need clarification known I've been seeing a lot of at one point I saw a question. Are you the one doing this? I've been seeing I could tell that you are Solomon are so busy right with this thing so what to know how it's how is because I assume and I appreciate that we are basically trying to build a very clear process and pipeline that produces the product respective of what you throw at it it produces the product that you
Hillary Arinda
yeah
Jerome Nuwabaasa
need. So how far are we with the pipeline?
Hillary Arinda
I'll go fast so I think what has made us progress. Is that a Solomon and his agent actually started using it before it was I mean nothing is completed until tested so through the testing the way a few holes that we've been patching up one at a time. So I'm always monitoring when I see something. I first Grant say what happened. What could have been done better? I close as they come so I'm sure a Solomon has not had the best of experiences like in the past week. I just want to know how things have.
If things have gotten better or are they getting worse?
Solomon Ariho
I can't say that they are getting worse. Because when I ask my I have gone like we are about to get through.
Hillary Arinda
okay
Solomon Ariho
When they tell you your stat here you're stuck here. That's when sometimes. I send you messages because they're asking me that that part should be done by Hillary
Hillary Arinda
Yes, and that is the part that helped when the two AI started critically each
Solomon Ariho
Hillary Arinda
other I started seeing things that had not earlier seen so it's a good thing what we started.
Solomon Ariho
So what I normally do is I ask my AI to do everything I can do on my side. before I studied to give you exactly the next instructions that are required to
Hillary Arinda
correct
Solomon Ariho
be done by Your Side
Hillary Arinda
okay But let's have not been getting a lot of instructions so and I'm seeing work on going. So does that mean we are? You're getting close.
Solomon Ariho
Now the problem is it tells you to wait?
Hillary Arinda
hmm
Solomon Ariho
And then after you've really waited for a long time. That's one of my thing it has failed so is that that time where you're not sure what is going on? because deployed
Hillary Arinda
Oh wait, your agent has no access to that.
Solomon Ariho
I don't receive from the WhatsApp messages you created.
Hillary Arinda
But you see now the thing is since you already have access to the backend as well your AI can see what's cool. Yeah, I can see what is happening not just on
Solomon Ariho
oh
Hillary Arinda
the front end, but on the back end.
Solomon Ariho
I'll probably give it the instruction to monitor that's to.
Hillary Arinda
Yeah, it should monitor because it has full access just like mine.
Solomon Ariho
I think very soon we shall be done with that pipeline maybe tomorrow.

🎯
Decision
Hillary Arinda
okay
Jerome Nuwabaasa
all right so
Hillary Arinda
I think but once you give it access to the logs and the whole infrastructure it will get much faster.
Solomon Ariho
okay
Jerome Nuwabaasa
all right so um so that means anything that you're doing Solomon Pushing it is not a pushing. It is not necessary that easy. Is there something that you've done that you walked on but they are currently not on the dashboard.
Solomon Ariho
Yeah, we've not yet. Gotten results on the dashboard except for one part where
Jerome Nuwabaasa
Because I see here I can tell you this was in there last time.
Solomon Ariho
I'd use. I worked in them.
Jerome Nuwabaasa
So they came through you pushed you walked on them and they they are on the dashboard, but this breakdown history.
Solomon Ariho
I walked on walked on. the key was no longer displaying the
Hillary Arinda
The names you don't even bring the name when you click on it has one daring.
Solomon Ariho
just so
Hillary Arinda
What was wrong?
Solomon Ariho
but I have not The names were just not displayed.
Hillary Arinda
Was it all is like that?
Solomon Ariho
No, it was like this so I noticed.
Hillary Arinda
So, how did they disappear hmm?
Solomon Ariho
I think that they disappeared during the changing of colors to this colors.
Hillary Arinda
Wait it had nothing to do with the database me. I thought it was a data base issue when we introduce pocket base.

✅
Action Item
Solomon Ariho
yeah no
Hillary Arinda
Okay, but these two some.
Jerome Nuwabaasa
This overlapping so many you see this overlapping. It's also a problem.
Hillary Arinda
cleaning
Jerome Nuwabaasa
Yeah, there is but that's you see me my views that once you've dealt with the
Hillary Arinda
yeah
Jerome Nuwabaasa
pipeline issue. Then the cleaning is.

✅
Action Item
Hillary Arinda
the easy pad
Jerome Nuwabaasa
yeah Because you you work on something they need to go through.
Hillary Arinda
Because at least the cleaning is totally dependent on you.
Jerome Nuwabaasa
Yes. yeah And and here someone I want us to change you see this is supposed to be a map the details are in the exploration. the value chain, Explorer So on the map, we will We Will mainly focus on the products from one stage to the other so mainly the inputs but will not but anyway we'll deal with that then for now. Let's finish the pipeline.
Hillary Arinda
Yeah, but at least what we want you can confirm is that all data is coming from pocket and that's a big win.
Jerome Nuwabaasa
okay That's good. That's good. so one other thing For today one. Okay so we huh. we wait Okay that means okay. I'll go ahead and work on something that I was okay. I'm already working with it, but I really want to make sure that. Our perfected it so I'm working on. In what they call metadat metadata?
Hillary Arinda
Yeah, we work with metadata every day. Yes.
Jerome Nuwabaasa
Wait, let me understand. How do you describe metadata from you say?
Hillary Arinda
due to the describes an object for example the data of a picture is the date

✅
Action Item
location at the format if
Jerome Nuwabaasa
Okay so yeah, but that's basically it's so when you say manufacturing value added they supposed to be what data describes. How do you come up with this manufacturing value added? So you you have the you let's say the manufacturing value added is a It the contribution of the value of manufacturing. So, it's actually the value of manufacturing which is calculated and then there is a filing new boss in which it is.
so you you basically describe that this let me see if I can find this Excel That I'm working on. It this one. I think let me just I want because this is what we had I had initially worked by one to make it even more better details so number of operations operate operational Industrial Park see. Is it says current 8 confirmed in uis summary report of this? It's like where

💡
Callout
are you getting this information? So what I want to is at least for these. This is not cleaned up properly but at least for these. I want that with is it in caters, but basically do it for as much data as I can I want to be very clear that this is how you calculate this and you get the data to do that calculation from here. and then I put together all those files and then I send them to Solomon For him to upload so everything will be clear that even if you asked it. How are you coming up with this figure? It will tell you I'm getting this figure by calculating it using this formula, which I was given and I am getting the data for that formula from this file.
So that yeah, so that shouldn't it makes because that's literally what I do. So
Hillary Arinda
accents
Jerome Nuwabaasa
once I train it essentially what I do like. I my job is to do these analysis and I have the formulas that I use when I must formula negative data from here. So once I have trained it then all I have to do is to in fact. I would have even told it where the data cable comes from so it but since we are uploading and now our phone that most of these documents I can actually find them and send them Solomon for uploading.
So, what's the pipeline is actually working well, then, there's no problem. So I'll go ahead and work on that as you finish the pipeline. I'll go ahead and try to finish that and
Hillary Arinda
So the metadata will be about. different cards that have been shown here or
Jerome Nuwabaasa
Yeah, so it will be about all these different cards each of these different cards. Will have the metadata.
Hillary Arinda
okay
Jerome Nuwabaasa
And then also these other indicators will also have the metadata. This one is just an analysis of data Solomon I hope you remember that here we
Solomon Ariho
Yep.
Jerome Nuwabaasa
are agreed that you just put icons, but you do not put the names.
Solomon Ariho
you didn't recognize but
Hillary Arinda
That seems like in fruit. That looks like yellow hanging fruit that effort to be cleared by now.
Solomon Ariho
I think
Jerome Nuwabaasa
because
Hillary Arinda
At any maybe it's saving the easiest for the last.
Jerome Nuwabaasa
Okay then you see what you did here with the break because you see if I come to beverages it has different.
Solomon Ariho
mmm
Jerome Nuwabaasa
so
Hillary Arinda
What is this what what is that?
Jerome Nuwabaasa
so yeah
Hillary Arinda
first click there again
Jerome Nuwabaasa
so
Hillary Arinda
There is a is it me or is the contrast issue.

✅
Action Item
Jerome Nuwabaasa
There's a contrast issue, so I think what you do solomoni.

✅
Action Item
When someone you see when someone goes into when someone goes into central okay, it should all be one color. Just subdivided. the difference in colors before regions You see how it is here. It's one color.
Solomon Ariho
mmm
Jerome Nuwabaasa
Subdivided keep it one color but subdivided. now if you
Hillary Arinda
Okay when you click just executed, please click into come central again. Something I saw yeah there, so what happens here in the legend. The Legend is anyway, is it really important?

💡
Callout
Solomon Ariho
ovies I think
Jerome Nuwabaasa
What this?
Solomon Ariho
Okay was I put the LED gems there is the district with the number because some are so tiny. You might miss them. When you're calling on the map.
Hillary Arinda
Yeah, that's true. So it has value. So what do we do?
Jerome Nuwabaasa
hmm this one
Hillary Arinda
Hey those ones because they've been the same color.
Solomon Ariho
I want to put
Jerome Nuwabaasa
It should be the same color.
Hillary Arinda
So that means you.
Solomon Ariho
Yeah, nothing about the number. I'm talking about the names of the districts and
Jerome Nuwabaasa
hmm
Solomon Ariho
in front of it is the number because some
Jerome Nuwabaasa
A1 compiler to aquisu three mokono like that.
Solomon Ariho
Normal Kampala having 3280 then there is like one or two.
Jerome Nuwabaasa
hmm
Hillary Arinda
Guys know that beer yes.
Solomon Ariho
next
Hillary Arinda
that one
Jerome Nuwabaasa
How did you know it was gumba?
Solomon Ariho
it's at the end, there is the
Jerome Nuwabaasa
yeah
Solomon Ariho
legend
Jerome Nuwabaasa
Hey, so nice by number.
Solomon Ariho
Yes.
Hillary Arinda
Oh, yeah, okay.
Solomon Ariho
so I want to
Jerome Nuwabaasa
No, but you don't need you don't need to do that because you see if I click here on the Antoni it will give me the upgrade.
Solomon Ariho
Done that click on this it will give you things now you're going on the unders changing on this on the right.
Jerome Nuwabaasa
Yes.
Solomon Ariho
Is changing sector distribution?
Jerome Nuwabaasa
Yes.
Solomon Ariho
I'm talking about the number of establishment in the
Jerome Nuwabaasa
But I see them they are here.
Solomon Ariho
saying
Jerome Nuwabaasa
Now what that is what doing?
Hillary Arinda
But it's not aggregated today.
Solomon Ariho
hmm
Jerome Nuwabaasa
They were putting another number on top here. the guys we copied
Hillary Arinda
aggregation okay
Jerome Nuwabaasa
Another number on top here which would always be the total so if I click to command CMB it would show me Siri they need to show me. So you see how District you see solo your district is Gabby here comes in me, so if you want to put the number put it here next to command symbi not in the legend but here.
Hillary Arinda
So now my question is what happens the Legend and the coloring if I go to well you're saying this should all be bubble.
Jerome Nuwabaasa
The legend yeah, it should all be purple.
Solomon Ariho
yeah
Hillary Arinda
hey
Jerome Nuwabaasa
And maybe this would says before the legend are not necessary. I don't know you
Hillary Arinda
so what does
Jerome Nuwabaasa
can find what else so you can leave them, but they should all be one.
Solomon Ariho
what the colors on the region
Hillary Arinda
You have you thought of very well about the color thing.
Jerome Nuwabaasa
You think it's okay to have this differentiates.
Hillary Arinda
I thought it should be like. One primary color but different shades like it gets light as the numbers becomes
Jerome Nuwabaasa
This is this is what it does.
Hillary Arinda
more so for example Kampala should be darker than work ISO that's how I would think of it.
Jerome Nuwabaasa
Solo, have you got that?
Hillary Arinda
Yes.
Solomon Ariho
hmm
Jerome Nuwabaasa
he
Hillary Arinda
Like how they paint population you see red then you get slighter like that it
Jerome Nuwabaasa
Yeah, use that use that.
Hillary Arinda
gives you a quicker picture of oh this one yes.
Jerome Nuwabaasa
The darkest should be eh. Yeah, use that. And do the same this side.
Hillary Arinda
But then we need to watch the contrast now like white against yellow now on my screen. I can barely see.
Jerome Nuwabaasa
yeah
Hillary Arinda
I don't know if it's my screen ish.
Solomon Ariho
things should we maybe Black
Jerome Nuwabaasa
So tell it to deal with the contrast.
Solomon Ariho
yeah, it should have changed the word to Black
Jerome Nuwabaasa
To Black yes. But do the same the biggest one the biggest ones should be.
Solomon Ariho
Coming from Dark to lightest.
Jerome Nuwabaasa
data exactly okay But they should so, this is the he's the point what okay all sectors good. You see beverages has several under it so beverage should also be subdivided the way you subdivided the district the region if you'd also subdivide these.
Solomon Ariho
mmm okay
Jerome Nuwabaasa
Have but when you subdivided this. Hey, what have I done? Anyway here down on The Legend just icons. All right, so maybe one last question about this because right now. We are still working on the pipeline focus on that let me also handle is that I'm supposed to handle one more question Hillary
Hillary Arinda
Yes, please.
Jerome Nuwabaasa
What up this guy?
Hillary Arinda
sorry
Jerome Nuwabaasa
this guy asked me
Hillary Arinda
Ask me ask me. It's just an insta egg.
Jerome Nuwabaasa
This is you know this is the egg. Is causing a lot of excitement? It's causing serious excitement okay. Tell me at what point does it get to work? What needs to be done for it to work?
Hillary Arinda
No, it works just that it only gets better once you use it I think Solomon has the best knowledge from the King Farm app. So in right now Kim Farm up as improved because of comments but this comments come from usage, so I would need someone to really interact with it the best guy to do this would be Dennis my the game of wrinkle the guy was done.
Put the apps plus his biggest skill is in breaking things that you think are working yeah, so you give him you give him testsuit and then you leave him to
Solomon Ariho
proof
Hillary Arinda
work. He will break it into days and then that's how you improve.
Jerome Nuwabaasa
yeah Okay you know.
Hillary Arinda
So yeah, we need someone to test it.
Jerome Nuwabaasa
I have I have an impact. I had an intern not have I had an intern sometime, but it girl who was from Germany So apparently the Mercedes-Benz when it would release a new model. It would give that vehicle to young young campus students or interns from university who are very reckless drivers. To see him just bash it around the way you want so apparently there would be
Hillary Arinda
hey
Jerome Nuwabaasa
like you would see a young student coming to school with the latest model of Mercedes Benz eh this guy kumbe. They are interested in his third board driving skills. So they are checking safety features. They're checking all those things so they just give it to him. It has so many sensors on it. So they give it to him for about one month for each other and period of time he drives it and then the monitor and in the contrast with others that they were given to other people so you're You say that and you remind me of that person someone who's good at breaking.
Hillary Arinda
Yeah, so at least it can do basic things for example you can ask it. How many food products are in let's say Kampala it should be able to answer that because it has access to pocket base so it can run queries directly we at least it should.
Jerome Nuwabaasa
in
Solomon Ariho
cooking
Hillary Arinda
It keeps using the same things I'm going to change it. Before it was saying typing. Oh is that correct where is it?
Jerome Nuwabaasa
Yeah, that's correct. It's here.
Hillary Arinda
oh
Solomon Ariho
But I think maybe that's when they are say that they are training the AI then that what we're supposed to do.
Hillary Arinda
no, no here you're not really training training is basically training the way it's a totally different ball game
Jerome Nuwabaasa
but it does Because if you click Masai you can see. the breakdown
Hillary Arinda
Now this is what I would need so now. This is a This kind of pre-training is what I would need like I'm like how did you feel the answer this question? And then we give it more access but now the public facing one is not as much as the one on staging because I didn't want to give it so much power, so you'll find that the one on staging my answer such a question, but this one can't because like I said it was an Easter egg until we define what it should do and then you can give it as much power.
Jerome Nuwabaasa
okay
Hillary Arinda
Yeah, but at least the framework for it to work is already there that was the whole concept now the concept is that just you get the concept you can even draw some images.
Jerome Nuwabaasa
okay
Hillary Arinda
Yeah, so basically, it should be consistent for quickly navigating for example should also if I want to do this, where do I go?
Jerome Nuwabaasa
yeah
Hillary Arinda
Then quickly tells the way you should go.
Jerome Nuwabaasa
okay
Hillary Arinda
Yeah, like a real assistant and then the other part is to make it improve like
Jerome Nuwabaasa
okay
Hillary Arinda
another idea. I thought of like you give it a brain I user for example. That's that well that takes some effort in terms of storage and all but it's not a bad idea for example like you if you're using. This browser will as you can see we don't have this we don't have like. A user a signing user right we have a session for what is going one and we have
Jerome Nuwabaasa
mm-hmm
Hillary Arinda
a device so what we can do. Once you're in a device and if you're always going to log on the same device and you're using these two everyday. We pick you we make this thing compound every time you use it it studies. How what questions you asking it, then it goes back. That's improving learning you learning you that such that the more you use it the better answers you start getting and then the more usable the whole platform becomes and production is that query? Yes, so it's a you can can actually become very big like that. Yeah,
Jerome Nuwabaasa
Okay, we're dealing with that then.
Hillary Arinda
when it's when we have dealt with the course. Yeah.
Jerome Nuwabaasa
for now Yeah for now. Let's make sure that we have completed with the pipeline. So that's maybe what you guys are working on tomorrow.

🎯
Decision
Solomon Ariho
Feeding you presented this.
Jerome Nuwabaasa
hey
Solomon Ariho
Meeting you presented that ask me.
Jerome Nuwabaasa
Caffeine commissioner so it you said watch this thing. I told him he said that is what I want I said okay, but it's coming is it are you sure anyway, but I think it was the perfect thing for him because you see you see how how you can come and say masaka. Has you can come here for you you navigate you say okay central. I'm looking for masaka. Look for masaka here and you pick masaka.
Most people don't like they don't want to do this this three steps they want to come here and say how many Industries and what kind are they? That's what they want anything answers. So, they don't want to navigate. It's interesting how people are yeah. so yeah, it's one other thing I wanted to oh yes, Hillary Now now that the contracts are out. I want us to have to agree on what will be delivered in the month of July And then agree on who is supposed to do what and I also want to know very early
Hillary Arinda
well
Jerome Nuwabaasa
enough if they are going to be some approval bottlenecks in delivering whatever we need to be delivered in the month of July so that I can start dealing with them early enough because like I say it will be paying a monthly but at the end of the month. It will be based on this is what we agreed to deliver we deliver it. We provide the timesheets and then we will process the pavement so I don't want I want us to have a plan.
In fact because that's what I want to be talking to the commission and the PS about I see so the team is in place. We have agreed that at the end of this month. This is what we'll deliver and once it has been delivered. I will bring it to you with the request for payment and that's going to be structure. So we need to do that assign responsibilities to the different people and then they

✅
Action Item
begin so that thing I pushed my view is that at the end of this month we should have I don't know if it's too much to us, but we should have all the system specification documents. Is it too much?
Hillary Arinda
um
Jerome Nuwabaasa
For you timber.
Hillary Arinda
yeah, wait, there are some three documents we walked on there was the protocol
Jerome Nuwabaasa
That I exchange protocol.
Hillary Arinda
Data exchange yeah, then there was the user journey and then. Product description those marked as Dan and sealed or they need review.
Jerome Nuwabaasa
No, they have to be because first of all the user what I just sent to you is the user journey that has been kind of improved from the previous one. Now in principle in terms of Execution you know we agreed that we look at the whole thing. And once we've looked at the whole thing we ask ourselves. What is what do we need to build what is going to be built underways what roles be handled by ways, but roles will be now that will be in a meeting that I will I will handle.
And I can also make sure that it is a recorded meeting with so that we get because depending on your availability this meetings can take too long so I wouldn't want to. Waste your time in that meeting. no the
Hillary Arinda
Having a transcript would be good. Yeah.
Jerome Nuwabaasa
Yeah, government meetings. I also don't want to expose you to you know some of my people will ask questions and you'll be like you I guess But yeah, I know them so I'm okay. I'm okay with those questions, but I also always find you know the other day. I was with the commissioner in a meeting. And it was really a useless meeting. And I asked him at sir is this the best use of our time? And he said so wondering really it's only the two already here and it might look in polite for us to move out, but this is the best use of.
Solomon Ariho
You ain't the meeting with other people.
Jerome Nuwabaasa
yes, it was it was actually a meeting of Okay this you know our meetings are not well structured. They our meetings.
Hillary Arinda
that's a
Jerome Nuwabaasa
Our meetings of the ministry. Are not well structured and that's because you see we meet to like for us. We meet to fix issues. These guys meet and it's like they meet to come up with issues. Not even like issues to be fixed. No, it's like they just this one comes up with this this one comes up with this this one so I think the time when we really discovered that this was going out of hand.
Is when we have a clock in we have things for clocking in at the ministry like facial identification? So one guy said yes this thing doesn't recognize my face. And then the head of it was there so they need to became a whole discussion about how this guy has been an issue for some reason this thing. We we calibrate

✅
Action Item
and it misses the face again and we do it and we misses it again and it became a whole discussion about how could it be what you know and then the guy at one
Solomon Ariho
maybe
Jerome Nuwabaasa
time was saying. Don't know if these these um Vendetta against me you know it it really went it
Hillary Arinda
it became
Jerome Nuwabaasa
it became personal and you know and then the it person is a lady then she also tries to defend herself then commissioner deck.
Solomon Ariho
What I would say maybe it is a nose.
Jerome Nuwabaasa
Yeah, so anyways, so I think submitting can be like that at the ministry or even
Hillary Arinda
a ministry
Jerome Nuwabaasa
with water so I wouldn't want to expose you to that. I just want what I have
Hillary Arinda
so
Jerome Nuwabaasa
shared to be the user Jack
Hillary Arinda
I want just yeah feels that information from you. Just like I'm I also have to go back to my team and we will see that information on what we need to do. Yeah.
Jerome Nuwabaasa
with filtered professional Exactly, so what I have pushed to you. I need to go so what I pushed to you was both the questions that you asked me but also the user journey. I think
Hillary Arinda
Jerome Nuwabaasa
I don't know if my third process is okay, but I think you would start with the user journey. Basically say these are the things that I need to effect right from the beginning to the end. Okay if these are the things that I need to effect that's when they can work on the data exchange protocol, because who am I because in that there's also a clear list of the different entities you would integrate with so.
If I am integrating with so on so what data are we exchanging and how to deal
Hillary Arinda
Yeah like but we worked on.
Jerome Nuwabaasa
with structured?
Hillary Arinda
The previous discussions was it but things we had not thought about.
Jerome Nuwabaasa
Yes, yes if I'm integrating with so on so you know what kind of data. We and how
Hillary Arinda
yeah
Jerome Nuwabaasa
is it supposed to be structured and at each point what kind of data do I need to collect you know all of that so you could detail it a little bit more structurally a bit more. So essentially it would be if I had to do two different documents. I don't know if I would okay. Yeah, I could do two different documents then I would take those documents.
They use a journey and the data exchange protocol because I don't want you to now start designing how you going to build before I get I get approvals so I I
Hillary Arinda
by
Jerome Nuwabaasa
would take this it's not so much buy in it's small like. Okay, let's call it by because it's like I have to explain it to these people and then they understand it and where they think and where we have proposed something and the thing that it should be otherwise we change it then we have a
Hillary Arinda
mmm
Jerome Nuwabaasa
final this is how everything will flow this is what happens at each stage and once we have all those then you say okay, how do I build this? So that's that's why I want. Depending on how long it would take you you can let me know and then I can plan ahead and shade you a meeting so for example right now. I could show you a pitting for like. Let's see Thursday 23rd.
The other Thursday right, I never actually did for 23rd and 24th. I take that somewhere and take them through this entire thing. And ask them a way of think it needs to change the process needs to be different and once we have in then. I get back to you will filter the information. This is what they need to do and then you make those improvements and then we move forward.
But that would we would have delivered if we have the documents what we call
Hillary Arinda
okay
Jerome Nuwabaasa
what you would call the system specification documents that really define what we are going to build by the end of the of the month.
Solomon Ariho
do that
Jerome Nuwabaasa
By the end of July for me that would be a major deliverable and also think having them clearly also makes it much easier for you guys to build yeah now the
Hillary Arinda
Yeah of definitely.
Jerome Nuwabaasa
only other thing that.
Hillary Arinda
Actually on the integration but because scaffolding an MVP that is not dependent like when if we are stabbing by stabbing. I mean mocking are called let's say to MTN or mocking calls to all the other people integrity with within a week. We shall have something for you and I thought that madam makes sense. I thought we should have. A mockup like because we also need to decide to add to. Maybe this can be the next step once the system design docs are out.
Next thing before we even build is the look and feel and the flow so basically we are grown screens. We agree on fonts. We agree on how we shall transition from this page to the next all that is not really good. It's just the wireframe now. Yes once that is agreed on and stamped Boom now the front end developer
Jerome Nuwabaasa
okay
Hillary Arinda
stats. In meanwhile, the backend guy is are not blocked because for them. They are working on backend stuff and API calls so for them. They may start well we'll
Jerome Nuwabaasa
mmm
Hillary Arinda
both start at the same time but I would want the front end guy to first do the wireframes of what the final production look like before we actually do the actual code. I think that should be stepped to.
Jerome Nuwabaasa
okay
Hillary Arinda
then here the other things that we need provision for now like AWS That we need to start the discussions early other things that we need to start discussing Ali iOS remember when I asked if we are going to Gospel art for me iOS a bit in how they work first of all you need 99 dollars annual developer membership. I think for one person that should be enough like for deploying on their app store then it takes some time for them to agree, but that can come at the later time because takes about three days three days is more than we need but those are things we had not earlier thought of in the initial plan but now because of cross-platform coming in we had a discussion so I'm already in the documents, but I don't think I mean the documents already a lot, so I wouldn't have access to detox with them. They are for our side. We call them architectural decision records, so basically the way we're going to work is like this.
Uh before we start we take decisions and why we took the decisions we put it in document then as we work if a design changes now we also record that why did it change for audit purposes but yes to those are be good for you to see the
Jerome Nuwabaasa
okay
Hillary Arinda
January are taking so currently what I'm what we are really working on as a team at this. Architecture design documents on first of all what technologies are we going to use and why number two is how is what kind of security are we going to use and why what this thing Suites are going to use and why what security is coming to that we're going to use and why and I think all this will still fall into your something. I need to understand. Clearly is there a difference between system design document and system specifications document. It's currently my class has
Jerome Nuwabaasa
no
Hillary Arinda
been on system designed document.
Jerome Nuwabaasa
Is this the same?
Hillary Arinda
It's the same. I'll then that's good news was really that's my current Focus I let you work on the user journey and until it's ready such that now I could come and feed it into the system design you get a yes, because I based on how you
Jerome Nuwabaasa
Yes.
Hillary Arinda
answered my questions, they would heavily. pin on what systems what design we're going to use
Jerome Nuwabaasa
okay
Hillary Arinda
I know this is a lot of yap, but basically that is what we are doing with the team. Everyone is deciding which tools and why once that is yes once that is.
Jerome Nuwabaasa
Now that's important. That's important and the fact that you you put it down.

💡
Callout
Hillary Arinda
is
Jerome Nuwabaasa
that's a very important thing because it's it's

💡
Callout
Again, I know the you see everything that you're going to do will require to be approved by some kind of committee for you to actually do it.
Hillary Arinda
Okay then, that's why it's good that we had been what we are doing giving risk.

💡
Callout
Jerome Nuwabaasa
yeah It's good that you know yeah.
Hillary Arinda
Why yeah? Yeah, then what else did I want to say mmm? Yeah, the next thing that of course is the devops stuffy setting up the pipelines setting up the scrum stuff like basically. We have what we call epics a bit umbrella and epic is a basically but front end mobile development is a whole epic so under that epic. You know put stories for example as a user I want to login like this when I login. I want to login like this uh-huh then that comes a story then we break that story into the different tasks the actual units of work that they develop our work on so that's a very critical.
I'm also working on currently it tips generally because we don't have much time so I am working on all these that once but ideally it should be user journey, then a specifications document and then I break it into the agile framework in github and then after that we have skeleton setup for the applications but to be

✅
Action Item
honest we have already set up the skeletons because I it is independent of the other party whether you going to doesn't matter if you've locked down on the flat application. It's always going to start up in the same way, so you could as well just start on it. That's why it was repulsory
Jerome Nuwabaasa
okay
Hillary Arinda
this.
Jerome Nuwabaasa
okay
Hillary Arinda
But very flexible I just the one thing that I wouldn't want us to change is the coil languages because they are we shall have trouble because that's where we've spent most of the time initially we are going python and react but from this interactions. We have now switched. We are now going Java and flatter. Now changing decision would be very painful to my team. But they defense in depth is in the documents really once your guys read through you cannot say no yeah, so that's what we are doing so to answer your question. Yes. User journey you said next show me the calendar. User journey, you said 23rd right user genius systems specification document.
Jerome Nuwabaasa
Yes.
Hillary Arinda
yeah, that's a good deliverable so
Jerome Nuwabaasa
so I can share you a meeting for 23rd of July
Hillary Arinda
Yeah, yeah.
Jerome Nuwabaasa
okay
Hillary Arinda
So, I'm going to communicate the same to my team and then all for everyone I mean they put in the work. I just need more effort.
Jerome Nuwabaasa
okay
Hillary Arinda
yeah
Jerome Nuwabaasa
All right, so yeah, and then you will do for me the timesheet based on how much time you'd have put in leading up to anyway that will do at the end of the at the end of the month. We even have a administrator who's job is to follow up the requisitions for any funds that I needed.
Hillary Arinda
okay
Jerome Nuwabaasa
For anything, yeah.
Hillary Arinda
So about that now should gaze. In what was in the other guys contracts should they pay like so much focus on the amount that was quoted but they what should they expectation be like if you get my question?
Jerome Nuwabaasa
The that's I think it should be market best so you basically say I think he is a simple question is as simple as this. What team to deliver the things that I have asked? How much would you charge? do you have an idea maybe that's the first question now that's Because if you don't can also come up with that.
Hillary Arinda
To the I mean. The easiest idea is the current reference of what the guys and because what is per hour right, so that is really depends on how much so they would they switch answer that question is how much would you be within to be paid per hour? right
Jerome Nuwabaasa
How much would you be willing to be paid per hour or how much do you charge per hour?
Hillary Arinda
So how much do you charge per hour exactly yeah therefore most of these guys?
Jerome Nuwabaasa
okay, yeah
Hillary Arinda
The actually above $50 per hour, but they know this is here the above $50 per
Jerome Nuwabaasa
okay
Hillary Arinda
hour about 50 55 there at least that's Andrew and Justin yeah.
Jerome Nuwabaasa
yeah Okay, so even if they are at that price. So let's say they are above 50 dollars per the question is how many hours would they have put in? So when they say how many hours they have put in then we consider because I know Andrew's hour in our in terms of their amount of work that he does within one hour. they Conceptualization back here can be two days.
Hillary Arinda
correct
Jerome Nuwabaasa
If you look at what Uganda and developer will do for you in two days. It's basically based on for example. They work that I've done with you Hillary they work that you do in an hour. It will take two to three days for for our normal people to do. So for me, I still don't mind it's because it means that I can say you for you. You can say that to deliver this documents. I'll need to have invested. Let's say 15 hours. Or 20 hours of my time. If you are is $50. Okay, let's say you always $80.
Hillary Arinda
You know before you go on so sorry. Sorry before you go and see the contracts have an amount per day. Is that anything go by or not?
Jerome Nuwabaasa
Yes. Now that is just to to utilize. To pay to that's that's what we will utilize for reporting purposes.
Hillary Arinda
okay
Jerome Nuwabaasa
But but I want people to be paid based on their effort.
Hillary Arinda
okay
Jerome Nuwabaasa
Yeah, I want people to be paid based on their genuine effort, so that's why I was saying that if they attack activity you've put in and given that you the lead I expect you to help me with this because you'll be able to monitor how much time people have put in.
Hillary Arinda
alright
Jerome Nuwabaasa
But if you have put in 20 hours. That's too thousand dollars right. But that's 20 hours could be pivoted to about 30 days so I think uses how much 800.
Hillary Arinda
seven hundred
Jerome Nuwabaasa
Okay use it 700.
Hillary Arinda
mmm
Jerome Nuwabaasa
hey Should Be Higher So that's that divided by three. Hey, no, I said. three Wait a minute. seven hundred Let's say.
Hillary Arinda
so what and so for Chai
Jerome Nuwabaasa
So this would be like so you see if you worked for 20 hours. My understanding of like the amount of time you put in if you put 20 hours into something it could be equivalent to what someone here. I would do for like a month.
Hillary Arinda
all right
Jerome Nuwabaasa
So okay, maybe not even a month but let's say at least for like let's say. 15 days or 20 days
Hillary Arinda
mmm
Jerome Nuwabaasa
So that would be if you rate is a hundred dollars per hour. What is your current hourly rate?
Hillary Arinda
I know now. I'm with monthly salary India
Jerome Nuwabaasa
Indian food but so let me ask you're telling me so is Andrew's time fully
Hillary Arinda
Jerome Nuwabaasa
booked.
Hillary Arinda
Like does he work 8 hours a day yes?
Jerome Nuwabaasa
He works eight hours a day.
Hillary Arinda
Yes.
Jerome Nuwabaasa
So he's an extremely rich man.
Hillary Arinda
It should be.
Jerome Nuwabaasa
Because at over 50 dollars an hour eight hours a day. That's quite a lot of
Hillary Arinda
Hey Rich I think even clear this loan already for school.
Jerome Nuwabaasa
money. okay
Hillary Arinda
hmm
Jerome Nuwabaasa
You've not yet clears.
Hillary Arinda
I'm clear having
Jerome Nuwabaasa
okay Yeah, but anyway so um at so let's say you worked you put in at a hundred dollars per hour this would be $2000 okay. Maybe even you could find that you did work for three thousand dollars, but if you use 30 days to use the rate of 30 days. At 700 that would be about 5,700. So with the days, we can easily account and and pay.
Hillary Arinda
okay
Jerome Nuwabaasa
Yeah, it shouldn't be a problem.
Hillary Arinda
So what discussion should I have this gentlemen?
Jerome Nuwabaasa
yeah So, it's just a calculate your time. Okay maybe let me ask this.
Hillary Arinda
hmm
Jerome Nuwabaasa
It would maybe let's see okay, let's let's say to produce the system specific the system documents all the system documents that I needed before you start setting up. How many work hours combined man ours? Do you think would go into that?
Hillary Arinda
I'm calculate because I need to sync up with you and requirements as well, so if I include that time. usually it takes Like now for ABB but a b b is not a good example a bit Explorer now for like because the stuff is really complex since it's hardware based so for a b b find that just Gathering requirements. And take more than the month. But it's because it's a legacy that's working in Legal Style but for this based on what we already have. 40 hours, so that's when we find working days.
Jerome Nuwabaasa
So if it takes 40 hours for for each.
Hillary Arinda
Yep.
Jerome Nuwabaasa
How many you let me see? Andrew for guys right
Hillary Arinda
right
Jerome Nuwabaasa
40 times 4 And then we give it a rate of about. You said they are above $50, but how much is it give me an exact figure?
Hillary Arinda
to be honest
Jerome Nuwabaasa
Are they is it close to a hundred?
Hillary Arinda
No close at 50 then to 100 can be more 160.
Jerome Nuwabaasa
Okay, let's do 60. So this is about 9600 so roughly 10,000. for this systems so we can pay that 10,000 dollars that's it's it's yeah, but of course in Uganda Shillings So you can basically say that to deliver this and that's why I want us to work on on this thing. I want us to break it down into deliverables and said to deliver this. This is how much money we need as a team and you can discuss it internally and say this is how much money we need as a team given the amount of time with him for putting it.
Hillary Arinda
okay
Jerome Nuwabaasa
Then I agree with it, then you comment and once it is done. I will break it down basically this goes to Hillary this goes to so and so this goes to so on so but based on days and repaid.
Hillary Arinda
Okay so one question. the based on the effort can each
Jerome Nuwabaasa
hmm
Hillary Arinda
Is there a cup they shouldn't go beyond that's the question will come when I told him this is going to be output best based on our city like okay now. What does it mean for? for what we signed for Get the question so how do we do? How do I answer such a question?
Jerome Nuwabaasa
What do you mix? No, I don't understand the question and
Hillary Arinda
It's very clear for example mmm. It's clear that yes, it's you've been you've signed for a fee per day okay
Jerome Nuwabaasa
Because you've not signed for. exactly Yeah, so it it's it's the cup the infact think of it like I am hiring a team.
Hillary Arinda
depend on when you are. Yeah.
Jerome Nuwabaasa
The team will tell me so right now. You will be like in order to deliver this. This will take us 200 hours. And these 200 hours will be. at a rate of $60 so 200 times $60 Is that no 12,000 dollars? So I know that once this is delivered. I have to pay 12,000 dollars now in terms
Hillary Arinda
hmm
Jerome Nuwabaasa
of paper. I have to you can tell me yeah that tells us at dollars pay these to heal array
Hillary Arinda
The break it down.
Jerome Nuwabaasa
pay these to Andrew pay this to answer.
Hillary Arinda
That was the initial discussion we had I think it was about. I told them 50 to 60k.
Jerome Nuwabaasa
okay
Hillary Arinda
I think That is what we had discussed between you and I yet given me a higher figure, but I went with the low frequent just to see appetite. Yeah.
Jerome Nuwabaasa
yeah, yeah exact so so we we pay that okay once we paid out it's
Hillary Arinda
hmm
Jerome Nuwabaasa
Uh yeah you you tell us how we paid out and we paid out and the way for us the way we paid out is if Andrew spent. Andrews rate is maybe like 600.
Hillary Arinda
yeah
Jerome Nuwabaasa
it's so if Andrew is supposed to get six million, let's say
Hillary Arinda
mmm
Jerome Nuwabaasa
And he walked for this remember his at 600 which means six million must be 10 days, but he did this work in in five hours.
Hillary Arinda
all right hmm
Jerome Nuwabaasa
For us we shall say he did the work in 10 days and pay him for his 10 days.
Hillary Arinda
index okay under split
Jerome Nuwabaasa
That's the bottom right.
Solomon Ariho
10 days or why you put 20 and he Returns the other 10 days?
Jerome Nuwabaasa
That's a whole complete different story right now. I want first make sure that they are covered in terms of and in fact. I am hesitant to start doing that before we've met some significant progress.
Hillary Arinda
I alsoons okay so for all I know from this discussion our first milestone is the
Jerome Nuwabaasa
Yeah, you see mmm.
Hillary Arinda
necessary document to start working and we have to Simple
Jerome Nuwabaasa
if exact Exactly and you have two weeks yeah, but if you can squeeze it and deliver it
Hillary Arinda
okay
Jerome Nuwabaasa
even a short period of time.
Hillary Arinda
Well, that's my goal because what I really needed was the user journey. No even

🎯
Decision
there is a remember our biggest point of confusion is not really the journey, but it's on who does what that's really well visual needs. Yeah.
Jerome Nuwabaasa
that is in fact that we have not yet resolved, but we need the user genetary resolve that that's why I want you to go through the user journey, what's

✅
Action Item
Hillary Arinda
okay Yeah, I'm going to go through by tonight and tomorrow.

🎯
Decision
Jerome Nuwabaasa
okay
Hillary Arinda
I've been to use this time, but now this time has been used for something bigger, but it's okay.
Jerome Nuwabaasa
okay
Hillary Arinda
yeah
Jerome Nuwabaasa
I think in that's it.
Hillary Arinda
So and I think we have a clear understanding.
Jerome Nuwabaasa
hmm
Hillary Arinda
Yeah, and he delivers from tonight.

🎯
Decision
Jerome Nuwabaasa
oh And no you guys just need to complete the pipeline.
Hillary Arinda
Yeah, so any issue you get you directly reach out there like they don't wait for

✅
Action Item
Jerome Nuwabaasa
Make sure things things are able to go through.
Hillary Arinda
me to ask if that's okay. hmm
Jerome Nuwabaasa
Solo this one is your project. So if there is any any issues, you are the problem.
Solomon Ariho
hey
Jerome Nuwabaasa
This one is your project. It's a yeah. You have to at least if there's any issue. We say it's your problem, then you are able to say no the problem is just because I ask you for this end. If not yet delivered it, but they probably kids

✅
Action Item
Hillary Arinda
the
Jerome Nuwabaasa
with you.
Hillary Arinda
pressure
Jerome Nuwabaasa
yeah yeah
Solomon Ariho
Hillary Arinda
Okay guys, I don't know if we need minutes for this, but I'll have my discussed
Jerome Nuwabaasa
okay okay
Hillary Arinda
many things that now going to YouTube back not an idd but we'll see the fine.
Jerome Nuwabaasa
yeah okay Okay guys, thank you.
Hillary Arinda
Okay, thank you. Alright, bye.

