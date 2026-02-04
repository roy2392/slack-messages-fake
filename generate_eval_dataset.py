#!/usr/bin/env python3
"""
Evaluation Dataset Generator
Creates evaluation datasets from Slack fake conversations
"""

import json
import csv
from datetime import datetime
from send_fake_messages import FAKE_CONVERSATIONS


def flatten_conversation():
    """Flatten the conversation into a list of messages with metadata"""
    messages = []
    message_id = 1

    for conv in FAKE_CONVERSATIONS:
        for msg in conv["messages"]:
            messages.append({
                "id": message_id,
                "username": conv["username"],
                "text": msg,
                "icon": conv["icon_emoji"]
            })
            message_id += 1

    return messages


def get_full_conversation_text():
    """Get the full conversation as a single text"""
    messages = flatten_conversation()
    return "\n".join([f"{msg['username']}: {msg['text']}" for msg in messages])


# Evaluation dataset with different task types
EVAL_DATASET = [
    # Question Answering - Extractive
    {
        "task_type": "question_answering",
        "sub_type": "extractive",
        "question": "What was the error rate that Alice reported seeing in production?",
        "answer": "2.3%",
        "context": "The error rate is around 2.3% since yesterday's deployment.",
        "difficulty": "easy"
    },
    {
        "task_type": "question_answering",
        "sub_type": "extractive",
        "question": "What was the incident ticket number created by Alice?",
        "answer": "INC-2847",
        "context": "I'm creating an incident ticket - INC-2847",
        "difficulty": "easy"
    },
    {
        "task_type": "question_answering",
        "sub_type": "extractive",
        "question": "What was the connection pool max size that caused the issue?",
        "answer": "10 (should have been 50)",
        "context": "Found it! The connection pool max size was set to 10, should be 50.",
        "difficulty": "medium"
    },
    {
        "task_type": "question_answering",
        "sub_type": "extractive",
        "question": "What is the URL of the test authentication environment?",
        "answer": "https://test-auth.company.com",
        "context": "The test env is: https://test-auth.company.com",
        "difficulty": "easy"
    },

    # Question Answering - Abstractive
    {
        "task_type": "question_answering",
        "sub_type": "abstractive",
        "question": "What was the root cause of the timeout errors in production?",
        "answer": "The database connection pool max size was incorrectly set to 10 instead of 50 in the application.yml file, which was overwritten during the last merge.",
        "difficulty": "medium"
    },
    {
        "task_type": "question_answering",
        "sub_type": "abstractive",
        "question": "How did the team resolve the production incident?",
        "answer": "Bob identified that the connection pool size was misconfigured and deployed a fix to change it from 10 to 50, which resolved the timeout errors within 3 minutes.",
        "difficulty": "medium"
    },
    {
        "task_type": "question_answering",
        "sub_type": "abstractive",
        "question": "What improvements did the team suggest to prevent similar incidents?",
        "answer": "The team suggested adding the configuration check to the deployment checklist, updating the runbook with troubleshooting steps, and implementing automated testing for configuration changes.",
        "difficulty": "hard"
    },

    # Sentiment Analysis
    {
        "task_type": "sentiment_analysis",
        "text": "Great catch Bob! 👏",
        "sentiment": "positive",
        "confidence": "high",
        "speaker": "Diana"
    },
    {
        "task_type": "sentiment_analysis",
        "text": "I'm seeing some timeout errors in production logs. Anyone else experiencing this?",
        "sentiment": "concerned",
        "confidence": "high",
        "speaker": "Alice"
    },
    {
        "task_type": "sentiment_analysis",
        "text": "Should we roll back the deployment? Our SLA is at risk if this continues.",
        "sentiment": "urgent/worried",
        "confidence": "high",
        "speaker": "Charlie"
    },
    {
        "task_type": "sentiment_analysis",
        "text": "Perfect team work everyone! 🎉",
        "sentiment": "positive",
        "confidence": "high",
        "speaker": "Diana"
    },
    {
        "task_type": "sentiment_analysis",
        "text": "Pretty excited about this one! 📊",
        "sentiment": "positive/excited",
        "confidence": "high",
        "speaker": "Alice"
    },

    # Named Entity Recognition
    {
        "task_type": "named_entity_recognition",
        "text": "I'm creating an incident ticket - INC-2847",
        "entities": [
            {"text": "INC-2847", "type": "TICKET_ID", "start": 32, "end": 40}
        ]
    },
    {
        "task_type": "named_entity_recognition",
        "text": "The test env is: https://test-auth.company.com",
        "entities": [
            {"text": "https://test-auth.company.com", "type": "URL", "start": 17, "end": 47}
        ]
    },
    {
        "task_type": "named_entity_recognition",
        "text": "We'll do a kickoff meeting next Monday to discuss architecture.",
        "entities": [
            {"text": "next Monday", "type": "DATE", "start": 31, "end": 42}
        ]
    },
    {
        "task_type": "named_entity_recognition",
        "text": "We're considering AWS Personalize, Google Recommendations AI, and a custom solution.",
        "entities": [
            {"text": "AWS Personalize", "type": "TECHNOLOGY", "start": 18, "end": 33},
            {"text": "Google Recommendations AI", "type": "TECHNOLOGY", "start": 35, "end": 60}
        ]
    },

    # Conversation Summarization
    {
        "task_type": "summarization",
        "sub_type": "extractive",
        "input": get_full_conversation_text(),
        "summary": "The team identified and resolved a production incident caused by incorrect database connection pool settings. They discussed sprint demos, new Q2 features including AI-powered recommendations, and technology evaluation options.",
        "key_points": [
            "Production timeout errors with 2.3% error rate",
            "Root cause: connection pool size set to 10 instead of 50",
            "Issue resolved in 3 minutes by deploying configuration fix",
            "Team will add automated testing for configuration changes",
            "Sprint review scheduled for tomorrow at 2 PM",
            "Q2 roadmap approved: AI recommendations and real-time notifications",
            "Evaluating AWS Personalize, Google Recommendations AI, and custom solutions"
        ]
    },

    # Intent Classification
    {
        "task_type": "intent_classification",
        "text": "Quick question about the new authentication service.",
        "intent": "inquiry",
        "sub_intent": "technical_question"
    },
    {
        "task_type": "intent_classification",
        "text": "Should we roll back the deployment?",
        "intent": "suggestion",
        "sub_intent": "risk_mitigation"
    },
    {
        "task_type": "intent_classification",
        "text": "I'll send a calendar invite in a few minutes.",
        "intent": "action_commitment",
        "sub_intent": "meeting_scheduling"
    },
    {
        "task_type": "intent_classification",
        "text": "Anyone available to help test today?",
        "intent": "request",
        "sub_intent": "assistance_needed"
    },
    {
        "task_type": "intent_classification",
        "text": "I'll share the PRD (Product Requirements Document) by end of week.",
        "intent": "commitment",
        "sub_intent": "document_sharing"
    },

    # Task Extraction
    {
        "task_type": "task_extraction",
        "conversation_segment": get_full_conversation_text(),
        "extracted_tasks": [
            {
                "task": "Complete post-mortem document for the production incident",
                "assignee": "Bob",
                "due": "EOD",
                "status": "committed"
            },
            {
                "task": "Add configuration check to deployment checklist",
                "assignee": "Diana",
                "due": "not specified",
                "status": "planned"
            },
            {
                "task": "Add automated testing for configuration changes to backlog",
                "assignee": "Bob",
                "due": "not specified",
                "status": "planned"
            },
            {
                "task": "Prepare demo for sprint review (analytics dashboard)",
                "assignee": "Charlie",
                "due": "tomorrow at 2 PM",
                "status": "in_progress"
            },
            {
                "task": "Help test authentication flow",
                "assignee": "Charlie",
                "due": "today at 1:30 PM",
                "status": "committed"
            },
            {
                "task": "Send test environment details via email",
                "assignee": "Bob",
                "due": "today",
                "status": "committed"
            },
            {
                "task": "Share PRD by end of week",
                "assignee": "Diana",
                "due": "end of week",
                "status": "committed"
            },
            {
                "task": "Research AI recommendation options",
                "assignee": "Alice",
                "due": "before kickoff meeting",
                "status": "planned"
            },
            {
                "task": "Prepare comparison matrix for recommendation services",
                "assignee": "Alice",
                "due": "before kickoff meeting",
                "status": "planned"
            }
        ]
    },

    # Temporal Reasoning
    {
        "task_type": "temporal_reasoning",
        "question": "How long did it take to deploy the fix for the connection pool issue?",
        "answer": "3 minutes",
        "reasoning": "Bob said 'ETA 3 minutes' when deploying the fix"
    },
    {
        "task_type": "temporal_reasoning",
        "question": "When is the sprint review scheduled?",
        "answer": "Tomorrow at 2 PM",
        "reasoning": "Diana mentioned 'our sprint review is tomorrow at 2 PM'"
    },
    {
        "task_type": "temporal_reasoning",
        "question": "When will Diana share the Product Requirements Document?",
        "answer": "By end of week",
        "reasoning": "Diana said 'I'll share the PRD by end of week'"
    },
    {
        "task_type": "temporal_reasoning",
        "question": "What time did Charlie offer to help test?",
        "answer": "After lunch, around 1:30 PM",
        "reasoning": "Charlie said 'I can help test after lunch, around 1:30 PM?'"
    },

    # Technical Knowledge Questions
    {
        "task_type": "technical_knowledge",
        "question": "What configuration parameter caused the production issue?",
        "answer": "Database connection pool max size",
        "context": "The connection pool max size was set to 10, should be 50"
    },
    {
        "task_type": "technical_knowledge",
        "question": "What authentication protocol is being implemented?",
        "answer": "OAuth2",
        "context": "I'll demo the new user authentication flow with OAuth2 support"
    },
    {
        "task_type": "technical_knowledge",
        "question": "What file contained the incorrect configuration?",
        "answer": "application.yml",
        "context": "It's in the application.yml file that got overwritten during the last merge"
    },
    {
        "task_type": "technical_knowledge",
        "question": "What services are being evaluated for AI recommendations?",
        "answer": "AWS Personalize, Google Recommendations AI, and a custom solution",
        "context": "We're considering AWS Personalize, Google Recommendations AI, and a custom solution"
    },

    # Multi-hop Reasoning
    {
        "task_type": "multi_hop_reasoning",
        "question": "What was the improvement in API response time and who will be presenting it?",
        "answer": "40% improvement, presented by Alice",
        "reasoning": "Alice said 'We reduced API response time by 40% on average' and 'I'll be presenting the performance improvements we made'",
        "difficulty": "medium"
    },
    {
        "task_type": "multi_hop_reasoning",
        "question": "Who has previous experience with AWS Personalize and how will they contribute?",
        "answer": "Bob has experience with AWS Personalize from his previous company and will share insights during the meeting",
        "reasoning": "Bob mentioned 'I have some experience with AWS Personalize from my previous company' and 'Happy to share insights during the meeting'",
        "difficulty": "medium"
    },

    # Relationship Extraction
    {
        "task_type": "relationship_extraction",
        "relationships": [
            {
                "entity1": "Alice",
                "relation": "reported",
                "entity2": "timeout errors",
                "confidence": "high"
            },
            {
                "entity1": "Bob",
                "relation": "fixed",
                "entity2": "connection pool issue",
                "confidence": "high"
            },
            {
                "entity1": "Charlie",
                "relation": "will_demo",
                "entity2": "analytics dashboard",
                "confidence": "high"
            },
            {
                "entity1": "Diana",
                "relation": "manages",
                "entity2": "sprint review",
                "confidence": "high"
            },
            {
                "entity1": "Bob",
                "relation": "has_experience_with",
                "entity2": "AWS Personalize",
                "confidence": "high"
            }
        ]
    },

    # Action Items Classification
    {
        "task_type": "action_items",
        "priority": "high",
        "items": [
            {
                "action": "Complete post-mortem document",
                "owner": "Bob",
                "deadline": "EOD",
                "type": "documentation"
            },
            {
                "action": "Test authentication flow",
                "owner": "Charlie",
                "deadline": "1:30 PM today",
                "type": "testing"
            }
        ]
    },
    {
        "task_type": "action_items",
        "priority": "medium",
        "items": [
            {
                "action": "Update deployment checklist",
                "owner": "Diana",
                "deadline": "not specified",
                "type": "process_improvement"
            },
            {
                "action": "Research AI recommendation options",
                "owner": "Alice",
                "deadline": "before kickoff",
                "type": "research"
            }
        ]
    }
]


def export_to_json(output_file="eval_dataset.json"):
    """Export evaluation dataset to JSON format"""
    data = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "conversation_source": "slack_fake_messages",
            "total_examples": len(EVAL_DATASET),
            "task_types": list(set([item["task_type"] for item in EVAL_DATASET]))
        },
        "conversation": {
            "messages": flatten_conversation(),
            "full_text": get_full_conversation_text()
        },
        "evaluation_data": EVAL_DATASET
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Exported evaluation dataset to {output_file}")
    return output_file


def export_to_csv(output_file="eval_dataset.csv"):
    """Export evaluation dataset to CSV format (simplified)"""
    rows = []

    for item in EVAL_DATASET:
        task_type = item.get("task_type", "")

        if task_type == "question_answering":
            rows.append({
                "task_type": task_type,
                "sub_type": item.get("sub_type", ""),
                "input": item.get("question", ""),
                "output": item.get("answer", ""),
                "context": item.get("context", ""),
                "difficulty": item.get("difficulty", "")
            })
        elif task_type == "sentiment_analysis":
            rows.append({
                "task_type": task_type,
                "sub_type": "",
                "input": item.get("text", ""),
                "output": item.get("sentiment", ""),
                "context": item.get("speaker", ""),
                "difficulty": ""
            })
        elif task_type == "intent_classification":
            rows.append({
                "task_type": task_type,
                "sub_type": item.get("sub_intent", ""),
                "input": item.get("text", ""),
                "output": item.get("intent", ""),
                "context": "",
                "difficulty": ""
            })
        elif task_type == "temporal_reasoning":
            rows.append({
                "task_type": task_type,
                "sub_type": "",
                "input": item.get("question", ""),
                "output": item.get("answer", ""),
                "context": item.get("reasoning", ""),
                "difficulty": ""
            })
        elif task_type == "technical_knowledge":
            rows.append({
                "task_type": task_type,
                "sub_type": "",
                "input": item.get("question", ""),
                "output": item.get("answer", ""),
                "context": item.get("context", ""),
                "difficulty": ""
            })

    if rows:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["task_type", "sub_type", "input", "output", "context", "difficulty"])
            writer.writeheader()
            writer.writerows(rows)

        print(f"✓ Exported simplified evaluation dataset to {output_file}")
        return output_file

    return None


def print_dataset_summary():
    """Print a summary of the evaluation dataset"""
    print("\n" + "=" * 60)
    print("EVALUATION DATASET SUMMARY")
    print("=" * 60)

    task_counts = {}
    for item in EVAL_DATASET:
        task_type = item.get("task_type", "unknown")
        task_counts[task_type] = task_counts.get(task_type, 0) + 1

    print(f"\nTotal Examples: {len(EVAL_DATASET)}")
    print(f"\nTask Type Distribution:")
    for task_type, count in sorted(task_counts.items()):
        percentage = (count / len(EVAL_DATASET)) * 100
        print(f"  - {task_type}: {count} ({percentage:.1f}%)")

    print(f"\nConversation Statistics:")
    messages = flatten_conversation()
    print(f"  - Total messages: {len(messages)}")
    print(f"  - Unique participants: {len(FAKE_CONVERSATIONS)}")
    print(f"  - Participants: {', '.join([c['username'] for c in FAKE_CONVERSATIONS])}")

    print("\n" + "=" * 60)


def main():
    """Main function"""
    print("=" * 60)
    print("EVALUATION DATASET GENERATOR")
    print("=" * 60)

    # Print summary
    print_dataset_summary()

    # Export to JSON
    print("\nExporting datasets...")
    json_file = export_to_json("eval_dataset.json")
    csv_file = export_to_csv("eval_dataset.csv")

    print("\n✅ Dataset generation complete!")
    print(f"\nFiles created:")
    print(f"  - {json_file} (full dataset with all fields)")
    print(f"  - {csv_file} (simplified format for basic tasks)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
