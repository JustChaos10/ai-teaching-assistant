"""
Module Executor - Executes teaching modules created by teachers
This system loads and runs custom teaching modules in the main application.
"""

import os
import json
import random
from typing import Dict, List, Any, Optional
from teacher_interface import TeachingModule

class ModuleExecutor:
    """
    Executes teaching modules created by teachers.
    Integrates with the main chatbot logic and game system.
    """
    
    def __init__(self, chatbot_logic=None):
        self.chatbot_logic = chatbot_logic
        self.active_modules = {}
        self.current_module = None
        self.current_question_index = 0
        self.load_active_modules()
    
    def load_active_modules(self):
        """Load all deployed teaching modules"""
        self.active_modules = {}
        
        # Load from active_modules directory
        active_dir = "active_modules"
        if os.path.exists(active_dir):
            for filename in os.listdir(active_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(active_dir, filename), 'r') as f:
                            module_data = json.load(f)
                            module = TeachingModule.from_dict(module_data)
                            self.active_modules[module.id] = module
                    except Exception as e:
                        print(f"Error loading active module {filename}: {e}")
        
        print(f"Loaded {len(self.active_modules)} active teaching modules")
    
    def get_available_modules(self) -> Dict[str, str]:
        """Get list of available modules with their titles"""
        return {module_id: module.title for module_id, module in self.active_modules.items()}
    
    def find_module_by_topic(self, user_input: str) -> Optional[TeachingModule]:
        """
        Find a relevant module based on user input.
        This matches keywords in the input to module titles, descriptions, and subjects.
        """
        user_input_lower = user_input.lower()
        
        best_match = None
        best_score = 0
        
        for module in self.active_modules.values():
            score = 0
            
            # Check title
            title_words = module.title.lower().split()
            for word in title_words:
                if word in user_input_lower:
                    score += 3
            
            # Check subject
            if module.subject in user_input_lower:
                score += 2
            
            # Check description
            desc_words = module.description.lower().split()
            for word in desc_words:
                if len(word) > 3 and word in user_input_lower:
                    score += 1
            
            # Check tags
            for tag in module.tags:
                if tag.lower() in user_input_lower:
                    score += 2
            
            if score > best_score:
                best_score = score
                best_match = module
        
        return best_match if best_score > 0 else None
    
    def start_module(self, module_id: str) -> str:
        """Start executing a specific module"""
        if module_id not in self.active_modules:
            return "Sorry, I couldn't find that learning module."
        
        self.current_module = self.active_modules[module_id]
        self.current_question_index = 0
        
        response = f"Great! Let's start learning about {self.current_module.title}!\n\n"
        response += f"{self.current_module.description}\n\n"
        
        if self.current_module.questions:
            response += self.get_next_question()
        
        return response
    
    def get_next_question(self) -> str:
        """Get the next question in the current module"""
        if not self.current_module or self.current_question_index >= len(self.current_module.questions):
            return self.complete_module()
        
        question_data = self.current_module.questions[self.current_question_index]
        question_text = question_data['question']
        
        response = f"Question {self.current_question_index + 1}: {question_text}\n\n"
        
        # Add instructions based on input method
        input_method = self.current_module.input_method.lower()
        if "placard" in input_method:
            response += "Show me a GREEN card for YES or a RED card for NO!"
        elif "finger" in input_method:
            response += "Show me the answer using your fingers!"
        elif "voice" in input_method:
            response += "Tell me your answer!"
        elif "choice" in input_method:
            response += "Choose your answer!"
        
        return response
    
    def process_answer(self, user_input: str) -> str:
        """Process the user's answer to the current question"""
        if not self.current_module:
            return "No active learning module. Let's start a new one!"
        
        if self.current_question_index >= len(self.current_module.questions):
            return self.complete_module()
        
        question_data = self.current_module.questions[self.current_question_index]
        
        # Process based on game type and input method
        is_correct = self.evaluate_answer(user_input, question_data)
        
        # Generate feedback
        if is_correct:
            feedback = random.choice([
                "Excellent work! That's absolutely correct! ⭐",
                "Fantastic! You got it right! 🎉",
                "Wonderful job! You're learning so well! 👏",
                "Perfect! That's the right answer! ✨",
                "Amazing! You're such a smart learner! 🌟"
            ])
        else:
            feedback = random.choice([
                "Good try! Let me help you understand this better. 💪",
                "That's a great attempt! Here's the correct answer: 📚",
                "Nice effort! Learning is all about trying. Let's see: 🤔",
                "Good thinking! The correct answer is: 💡",
                "You're learning so well! The right answer is: 🌱"
            ])
            
            # Add correct answer if available
            if 'correct_answer' in question_data:
                feedback += f" {question_data['correct_answer']}"
        
        # Move to next question
        self.current_question_index += 1
        
        # Check if module is complete
        if self.current_question_index >= len(self.current_module.questions):
            feedback += f"\n\n{self.complete_module()}"
        else:
            feedback += f"\n\n{self.get_next_question()}"
        
        return feedback
    
    def evaluate_answer(self, user_input: str, question_data: Dict) -> bool:
        """Evaluate if the user's answer is correct"""
        input_method = self.current_module.input_method.lower()
        game_type = self.current_module.game_type.lower()
        
        # Simple evaluation logic - can be enhanced based on question type
        if "classification" in game_type or "right/wrong" in game_type:
            # For yes/no questions
            user_lower = user_input.lower()
            if "yes" in user_lower or "correct" in user_lower or "right" in user_lower:
                return question_data.get('correct_answer', 'yes').lower() == 'yes'
            elif "no" in user_lower or "wrong" in user_lower or "incorrect" in user_lower:
                return question_data.get('correct_answer', 'no').lower() == 'no'
        
        elif "counting" in game_type:
            # Extract numbers from user input
            import re
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                user_number = int(numbers[0])
                correct_number = question_data.get('correct_answer', 0)
                return user_number == correct_number
        
        # Default: check if answer contains correct keywords
        correct_answer = str(question_data.get('correct_answer', '')).lower()
        return correct_answer in user_input.lower()
    
    def complete_module(self) -> str:
        """Complete the current module"""
        if not self.current_module:
            return ""
        
        module_title = self.current_module.title
        total_questions = len(self.current_module.questions)
        
        completion_message = f"""
🎊 Congratulations! You've completed the "{module_title}" learning module! 🎊

You answered {total_questions} questions and learned so much! 

I'm so proud of how hard you worked and how much you've learned today. 
You're becoming such a smart and curious learner! 

Would you like to try another learning activity, or do you have any questions about what we just learned?
        """
        
        # Reset current module
        self.current_module = None
        self.current_question_index = 0
        
        return completion_message.strip()
    
    def get_module_suggestions(self, subject: str = None) -> str:
        """Get suggestions for available modules"""
        if not self.active_modules:
            return "I don't have any custom learning modules available right now. But I can still help you learn about many topics!"
        
        suggestions = "Here are some exciting learning activities I have prepared for you:\n\n"
        
        for module_id, module in self.active_modules.items():
            if subject is None or module.subject.lower() == subject.lower():
                difficulty_stars = "⭐" * module.difficulty_level
                suggestions += f"📚 {module.title} {difficulty_stars}\n"
                suggestions += f"   {module.description}\n\n"
        
        suggestions += "Just tell me which one interests you, or say something like 'I want to learn about...' and I'll find the perfect activity!"
        
        return suggestions
    
    def handle_module_request(self, user_input: str) -> tuple[str, bool]:
        """
        Handle a request that might be asking for a teaching module.
        Returns (response, module_started)
        """
        user_lower = user_input.lower()
        
        # Check if user is asking for available modules
        if any(phrase in user_lower for phrase in ["what can you teach", "learning activities", "show modules", "what games"]):
            return self.get_module_suggestions(), False
        
        # Check if user wants to start a specific module
        if any(phrase in user_lower for phrase in ["start", "begin", "learn about", "teach me"]):
            matching_module = self.find_module_by_topic(user_input)
            if matching_module:
                response = self.start_module(matching_module.id)
                return response, True
        
        # Check if user is answering a question in an active module
        if self.current_module:
            response = self.process_answer(user_input)
            return response, True
        
        # No module interaction
        return "", False
    
    def is_module_active(self) -> bool:
        """Check if a module is currently active"""
        return self.current_module is not None
    
    def get_current_module_info(self) -> Optional[Dict]:
        """Get information about the current active module"""
        if self.current_module:
            return {
                'title': self.current_module.title,
                'subject': self.current_module.subject,
                'question_index': self.current_question_index,
                'total_questions': len(self.current_module.questions),
                'input_method': self.current_module.input_method
            }
        return None

# Integration helper function
def integrate_with_chatbot(chatbot_logic):
    """
    Integrate the module executor with the existing chatbot logic.
    This function modifies the chatbot to check for teaching modules.
    """
    executor = ModuleExecutor(chatbot_logic)
    
    # Store original get_response method
    original_get_response = chatbot_logic.get_response
    
    def enhanced_get_response(text: str) -> str:
        """Enhanced response that checks for teaching modules first"""
        # Check if this is a module-related request
        module_response, module_handled = executor.handle_module_request(text)
        
        if module_handled:
            return module_response
        
        # If no module handled it, use original chatbot logic
        original_response = original_get_response(text)
        
        # If no good response and we have modules, suggest them
        if len(original_response.strip()) < 50 and executor.active_modules:
            suggestion = executor.find_module_by_topic(text)
            if suggestion:
                original_response += f"\n\nI have a great learning activity about this topic: '{suggestion.title}'. Would you like to try it?"
        
        return original_response
    
    # Replace the method
    chatbot_logic.get_response = enhanced_get_response
    chatbot_logic.module_executor = executor
    
    return executor

if __name__ == "__main__":
    # Test the module executor
    executor = ModuleExecutor()
    print("Available modules:", executor.get_available_modules())
    
    # Test module finding
    test_input = "I want to learn about fruits and vegetables"
    module = executor.find_module_by_topic(test_input)
    if module:
        print(f"Found module: {module.title}")
        response = executor.start_module(module.id)
        print(f"Module response: {response}")
    else:
        print("No matching module found")