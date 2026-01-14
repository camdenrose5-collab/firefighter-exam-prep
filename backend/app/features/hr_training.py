"""
Human Relations Training Examples
Curated Q&A examples for training the AI to generate better Human Relations questions.
Source: User-provided training document

Key Patterns Identified:
1. TEAMWORK: Joining group activities, helping colleagues, not being lazy
2. DE-ESCALATION: Calming upset family members, redirecting hostile bystanders
3. CONFLICT RESOLUTION: Private conversations first, lowest level resolution
4. PATIENT CONSENT: Persuading without forcing, respecting autonomy
5. PROFESSIONALISM: Following policies, reporting concerns appropriately
"""

# Few-shot examples for Human Relations question generation
HR_TRAINING_EXAMPLES = [
    {
        "scenario": "Two cadets are trying to complete the air-pack drill in under 2 minutes. The rookie takes several attempts to finally finish the drill at 1m59s. The cadet tells the rookie that dinner isn't for another 30 min, and asks to go workout.",
        "question": "Choose the correct answer.",
        "options": [
            "Go workout until dinner",
            "Keep practicing the air-pack drill until dinner",
            "Tell your supervisor that you have completed your drill and are ready for the next task",
            "Relax until dinner"
        ],
        "correct_answer": "Keep practicing the air-pack drill until dinner",
        "explanation": "Barely passing (1:59 vs 2:00) means more practice is needed. A probie should use available time to improve skills rather than exercising or relaxing."
    },
    {
        "scenario": "You pull up to a medical response and there is a small crowd around an unconscious young boy. A lady comes at you yelling, 'GET UP HERE! COME ON! WHERE THE HECK HAVE YOU BEEN!'",
        "question": "How do you correctly respond to this woman?",
        "options": [
            "Tell her that this was a very fast response and the only person slowing it down is her",
            "Ask her to help you get the crowd moved back from the child so you can work",
            "Move directly to the injured child without saying more to the woman or anyone else",
            "Ask everyone in a nice way to please move back"
        ],
        "correct_answer": "Ask her to help you get the crowd moved back from the child so you can work",
        "explanation": "Redirect her energy productively. Giving her a task channels her anxiety into helping while clearing the scene. Don't argue or ignore - engage constructively."
    },
    {
        "scenario": "A fellow firefighter is cooking in the kitchen, and the garbage is completely full. A rookie walks in, asks when dinner will be ready, spits in the full trash can, sits around reading the newspaper while others help, then asks one of the firefighters to fetch the blood pressure pump.",
        "question": "What do you do?",
        "options": [
            "Offer to get the blood pressure pump. Later privately talk with the rookie that he should do more work so you both succeed",
            "Tell him right now to stop being so lazy",
            "Stay out of the whole situation. Let the experienced firefighters handle it",
            "Get the blood pressure pump and let your supervisor know about the extra work you are doing"
        ],
        "correct_answer": "Offer to get the blood pressure pump. Later privately talk with the rookie that he should do more work so you both succeed",
        "explanation": "Handle the immediate task, then address the behavior PRIVATELY. Public confrontation creates conflict; private coaching builds relationships and improves behavior."
    },
    {
        "scenario": "You pull up to a medical response when a guy walks over to you and says 'Hey man, I'm an EMT I can help'. He is clearly drunk.",
        "question": "What do you do?",
        "options": [
            "Say 'Thanks but we have everything under control.' Then ask him to move back",
            "Say 'You're not really in a good condition to help. I need you to move away'",
            "Address the whole crowd. Tell them to move back",
            "Tell the whole crowd to move back and make sure someone keeps that man back"
        ],
        "correct_answer": "Say 'Thanks but we have everything under control.' Then ask him to move back",
        "explanation": "Politely decline while preserving his dignity. No need to publicly call out his intoxication - just redirect professionally."
    },
    {
        "scenario": "Husband got shot in his home, and his wife is screaming at him while the fire medics are trying to work on him. The wife keeps screaming and arguing with the patient.",
        "question": "What do you do?",
        "options": [
            "One medic should ask the police officer to escort the wife away from her husband",
            "One medic should physically remove the wife from the room",
            "One medic should try to calm this couple down by helping resolve the argument",
            "Raise your voice and order the couple to stop arguing"
        ],
        "correct_answer": "One medic should ask the police officer to escort the wife away from her husband",
        "explanation": "Use available resources (police) to manage the scene. Don't physically engage or try to mediate a domestic argument - focus on patient care."
    },
    {
        "scenario": "A person in police custody from a domestic violence call needs medical treatment but refuses by saying, 'I know my rights, I don't want your help'.",
        "question": "How do you handle this?",
        "options": [
            "Try to convince him to accept treatment. Explain that you are only there to help treat his wound",
            "Tell the man if he wants to, you'll look at his arm. Otherwise, he can go with the officer",
            "Have the officer tell the man what his choices are",
            "Just tell the officer that the man has refused treatment"
        ],
        "correct_answer": "Try to convince him to accept treatment. Explain that you are only there to help treat his wound",
        "explanation": "Make a genuine effort to help. Explain your neutral role - you're there for medical care, not to judge or punish. Persuade without coercing."
    },
    {
        "scenario": "You walk in on a fellow firefighter in the locker room and notice his locker has a strong odor. He embarrassingly admits he hasn't had a chance to wash his workout clothes.",
        "question": "What do you do?",
        "options": [
            "Nothing. Just forget about it",
            "Have a serious private talk with him",
            "Remind him often to clean his clothes",
            "Tell your supervisor about the odor"
        ],
        "correct_answer": "Nothing. Just forget about it",
        "explanation": "This is a minor, one-time issue and he's already embarrassed. No need to escalate, lecture, or report. Let it go - picking battles is key."
    },
    {
        "scenario": "You are responding to a medical call where a man's wife called because her husband is having chest pains. The man is clearly adamant about not receiving help and says he is fine.",
        "question": "What do you do?",
        "options": [
            "Try to persuade the man to let you check him out to be sure he's okay",
            "Insist on checking him out",
            "Respect the man's wishes and leave",
            "Tell him to be more cooperative. You are concerned he is dying"
        ],
        "correct_answer": "Try to persuade the man to let you check him out to be sure he's okay",
        "explanation": "The man's pride is getting in the way of proper care. Work to get his consent by showing respect for his pride rather than forcing or abandoning him."
    },
    {
        "scenario": "You find out Mike has called in sick to work on Thanksgiving but you know he is actually in Jamaica and couldn't find coverage.",
        "question": "What do you do?",
        "options": [
            "Nothing else. Just work the shift",
            "Go back and tell the other firefighters that the Captain thinks Mike is sick",
            "Tell the Captain that Mike may really have gone to Jamaica. He was looking for relief but couldn't find one",
            "Talk to Mike directly when he returns and tell him how it affected you"
        ],
        "correct_answer": "Tell the Captain that Mike may really have gone to Jamaica. He was looking for relief but couldn't find one",
        "explanation": "This is not rumor-spreading - it's keeping leadership informed of legitimate management concerns. The Captain needs to know to make appropriate decisions."
    },
    {
        "scenario": "The Captain asks you and your coworker to set up the extension ladder together after your workout. Your coworker says he's done and will do it alone. Fire policy states extension ladder is a two-person job.",
        "question": "What do you do?",
        "options": [
            "Say that you've been assigned to work with him and you intend to follow orders",
            "Say that as a rookie you would like the practice, plus it's safer to work together",
            "Tell him you'd be glad if he changes his mind",
            "Just let the Captain know that he doesn't want you to help"
        ],
        "correct_answer": "Say that as a rookie you would like the practice, plus it's safer to work together",
        "explanation": "Frame it as YOUR need (wanting practice) rather than criticizing him. Shows good human relations by expressing it as if it would be a favor while ensuring safety compliance."
    },
    {
        "scenario": "You are looking for Jake to see if he wants to go workout with you. You find Jake is outside with the team helping clean the fire truck.",
        "question": "What do you do?",
        "options": [
            "Go outside and help clean the engine",
            "Go help clean the engine. Encourage everyone to work fast so you and Jake can get your workout in",
            "Ask Jake if he wants to go workout with you",
            "Don't bother Jake. Workout alone"
        ],
        "correct_answer": "Go outside and help clean the engine",
        "explanation": "Group work activity takes priority over personal improvement. Shows greater teamwork, industriousness, and professionalism to join the team effort first."
    },
    {
        "scenario": "You arrive at a scene with an unconscious patient. You see one of your mates take the patient's wallet and put it on top of his clipboard.",
        "question": "What do you do?",
        "options": [
            "Follow him and make sure he gives it to the supervisor",
            "Later ask the supervisor if he ever got the wallet",
            "Tell him he'd get in trouble if he doesn't turn the wallet in",
            "Take no action. Assume he will turn it in"
        ],
        "correct_answer": "Take no action. Assume he will turn it in",
        "explanation": "Placing the wallet on the clipboard is an open and secure way to carry it - not suspicious at all. Trust your colleague unless you have real reason not to."
    },
    {
        "scenario": "Another firefighter is annoyed and mad at you for leaving your clothes in the dryer, even though they JUST finished.",
        "question": "How do you respond?",
        "options": [
            "Say your laundry just finished and you didn't leave it for anyone else",
            "Just apologize and fold your clothes",
            "Apologize but say that the machine must've just stopped",
            "Tell the supervisor that this senior firefighter is giving you a hard time"
        ],
        "correct_answer": "Just apologize and fold your clothes",
        "explanation": "Goal is to resolve the situation quickly with no conflict. Don't argue about timing - just apologize and fix it. Avoid escalating minor friction."
    },
    {
        "scenario": "You are working under the truck with your squad when the Captain asks for a volunteer to take a Fire Safety class this weekend. Vet says 'Why don't you make the Rookies do it?' Rookie responds 'Wouldn't you want someone more experienced to do it?'",
        "question": "What do you do?",
        "options": [
            "Suggest a way to make it fair, maybe a rotating schedule",
            "Suggest to the rookie that the best way to get experience is to take chances like this",
            "Volunteer to take the assignment. Suggest the Rookie comes along for experience",
            "Stay out of it. Wait for the supervisor to decide"
        ],
        "correct_answer": "Volunteer to take the assignment. Suggest the Rookie comes along for experience",
        "explanation": "Shows industriousness and willingness to resolve a small impasse. Also shows consideration for helping the recruit get more comfortable with such assignments."
    },
    {
        "scenario": "You arrive on scene helping a woman with a possible broken arm, then your Captain tells you to go help your coworker with a more serious injury. The husband is yelling 'Where are you going?'",
        "question": "What do you do?",
        "options": [
            "Tell the man that he is not the one making decisions or giving orders here",
            "Just ignore him and go directly to assist with the other patient",
            "Tell the man to talk to the captain who is in charge here",
            "Tell the man that his wife will get help but you need to help the more severely injured patient first"
        ],
        "correct_answer": "Tell the man that his wife will get help but you need to help the more severely injured patient first",
        "explanation": "Brief reassurance calms them so they don't obstruct care of the critical patient. Explain triage priority - don't argue, redirect, or ignore."
    },
    {
        "scenario": "You are on a medical response in the middle of a park. Two random men come up and start asking questions about what you are doing.",
        "question": "What do you do?",
        "options": [
            "Tell them it's a medical aid response. Ask them to please stand back so you have more room",
            "Just tell them to move back and stop disrupting your work",
            "Tell them to move back. Tell them their interference could make the patient worse",
            "Politely explain the medical response steps you are taking"
        ],
        "correct_answer": "Tell them it's a medical aid response. Ask them to please stand back so you have more room",
        "explanation": "Brief answer to their question, polite instruction to move back. Maintains good public relations - no wasted argument or chastisement."
    },
    {
        "scenario": "You are studying in a room when the firefighter who was previously giving you a hard time walks in crying.",
        "question": "What do you do?",
        "options": [
            "Leave the room",
            "Mind your own business; focus on your work",
            "See if he will talk with you about what's wrong",
            "Suggest he go talk with the Captain"
        ],
        "correct_answer": "See if he will talk with you about what's wrong",
        "explanation": "Shows concern for fellow firefighters and compassion for a person in distress. Despite past friction, offering support builds relationships and demonstrates character."
    }
]

# Summary statistics for prompting
HR_PATTERNS = """
HUMAN RELATIONS KEY PATTERNS (Based on Training Data):

1. **PRIVATE FIRST**: Address coworker issues privately before escalating
2. **DE-ESCALATE**: Redirect hostile bystanders/family productively (give them a task)
3. **PERSUADE, DON'T FORCE**: For patient consent, respect autonomy while trying to help
4. **TEAM OVER SELF**: Join group activities before personal improvement
5. **TRUST COLLEAGUES**: Assume good intent unless you have real evidence otherwise
6. **BRIEF & PROFESSIONAL**: Short explanations, no arguments with public
7. **USE AVAILABLE RESOURCES**: Police for crowd control, supervisors for policy issues
8. **VOLUNTEER UP**: Take initiative to resolve impasses and help rookies learn
9. **APOLOGIZE & FIX**: Don't argue about minor issues - just resolve them
10. **SHOW COMPASSION**: Offer support even to difficult colleagues
"""

# Format examples for few-shot prompting
def format_hr_examples(num_examples: int = 3) -> str:
    """Format a subset of HR examples for use in prompts."""
    import random
    selected = random.sample(HR_TRAINING_EXAMPLES, min(num_examples, len(HR_TRAINING_EXAMPLES)))
    
    formatted = []
    for i, ex in enumerate(selected, 1):
        formatted.append(f"""
EXAMPLE {i}:
Scenario: {ex['scenario']}
Question: {ex['question']}
A) {ex['options'][0]}
B) {ex['options'][1]}
C) {ex['options'][2]}
D) {ex['options'][3]}
Correct Answer: {ex['correct_answer']}
Why: {ex['explanation']}
""")
    return "\n".join(formatted)
