#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-Enhanced IP Subnet Calculator Assistant

This module adds AI capabilities to the subnet calculator to provide:
1. Natural language explanations of subnetting concepts
2. Network planning assistance
3. Problem-solving guidance for complex networking scenarios

Author: Samir Rahman
Date: April 2025
"""

import json
import os
import sys
import argparse
from typing import Dict, List, Any, Optional
import ipaddress
from subnet_calculator import SubnetCalculator  # Import from existing module

# Import OpenAI library
try:
    from openai import OpenAI
except ImportError:
    print("OpenAI library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI

class SubnetAI:
    """
    AI-enhanced subnet calculator that uses OpenAI to provide intelligent
    assistance for network planning and subnet explanations.
    """
    
    def __init__(self, config_path: str = "config.json") -> None:
        """
        Initialize the SubnetAI with the OpenAI API key from a config file.
        
        Args:
            config_path: Path to configuration file with API key
        """
        self.config = self._load_config(config_path)
        self.client = self._initialize_openai()
        
    def _load_config(self, config_path: str) -> Dict[str, str]:
        """
        Load API key from config file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary containing configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _initialize_openai(self) -> OpenAI:
        """
        Initialize the OpenAI client with the API key.
        
        Returns:
            OpenAI client
        """
        api_key = self.config.get("openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key not found in configuration file")
            
        return OpenAI(api_key=api_key)
    
    def explain_subnetting_concept(self, concept: str) -> str:
        """
        Provide an explanation of a subnetting concept using AI.
        
        Args:
            concept: The subnetting concept to explain
            
        Returns:
            An explanation of the concept
        """
        prompt = f"""Explain the networking concept of "{concept}" related to IP subnetting. 
        Provide a clear, concise explanation that would help a networking student understand the concept.
        Include practical examples if relevant."""
        
        return self._get_ai_response(prompt)
    
    def plan_network(self, requirements: str) -> str:
        """
        Generate a network plan based on requirements.
        
        Args:
            requirements: Description of network requirements
            
        Returns:
            A network plan including recommended subnets and IP addressing
        """
        prompt = f"""As a network planning assistant, create a detailed IP addressing and subnetting plan based on these requirements:

        {requirements}
        
        Provide:
        1. IP address range selection with justification
        2. Subnet breakdown with sizes, masks, and usable ranges
        3. Network diagram description
        4. VLSM implementation if needed
        5. Any special considerations for routing or security
        
        Be specific with actual IP addresses and subnet masks."""
        
        return self._get_ai_response(prompt)
    
    def analyze_subnet_problem(self, problem: str) -> str:
        """
        Analyze a subnetting problem and provide steps to solve it.
        
        Args:
            problem: Description of the subnetting problem
            
        Returns:
            Step-by-step solution to the problem
        """
        prompt = f"""Analyze this IP subnetting problem and provide a detailed, step-by-step solution:

        {problem}
        
        Show all work including:
        1. Initial analysis of the problem
        2. Required calculations with formulas
        3. Working through each step with clear explanations
        4. Final solution with verification"""
        
        return self._get_ai_response(prompt)
    
    def get_quiz_question(self, difficulty: str = "medium") -> Dict[str, Any]:
        """
        Generate a subnetting quiz question for practice.
        
        Args:
            difficulty: Difficulty level ("easy", "medium", "hard")
            
        Returns:
            Dictionary containing question, answer, and explanation
        """
        prompt = f"""Generate a {difficulty} difficulty IP subnetting practice question. 
        The question should test understanding of subnet calculations, CIDR notation, or IP address allocation.
        
        Return in this exact JSON format:
        {{
            "question": "The question text",
            "answer": "The correct answer",
            "explanation": "Detailed explanation of how to solve the problem"
        }}"""
        
        response = self._get_ai_response(prompt)
        
        try:
            # Parse the response as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            return {
                "question": "Generated question might not be in correct format",
                "answer": "See explanation",
                "explanation": response
            }
    
    def troubleshoot_subnet_issue(self, issue_description: str) -> str:
        """
        Provide troubleshooting guidance for subnet-related issues.
        
        Args:
            issue_description: Description of the networking issue
            
        Returns:
            Troubleshooting steps and potential solutions
        """
        prompt = f"""As a network troubleshooting assistant, analyze this subnet-related issue and provide detailed troubleshooting steps:

        {issue_description}
        
        Include:
        1. Potential causes of the issue
        2. Step-by-step troubleshooting procedure
        3. Commands to use for diagnosis (with syntax)
        4. Potential solutions for each likely cause
        5. Best practices to prevent this issue in the future"""
        
        return self._get_ai_response(prompt)
    
    def _get_ai_response(self, prompt: str) -> str:
        """
        Get a response from the OpenAI API.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            The API response
            
        Raises:
            Exception: If there's an error with the API request
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Using advanced model for technical accuracy
                messages=[
                    {"role": "system", "content": "You are an expert networking assistant specializing in IP addressing, subnetting, and network design. Provide technically accurate, clear, and educational responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more deterministic, factual responses
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error getting AI response: {str(e)}"


def display_explanation(explanation: str) -> None:
    """
    Display an explanation with nice formatting.
    
    Args:
        explanation: Text to display
    """
    width = min(100, os.get_terminal_size().columns)
    print("\n" + "=" * width)
    print(explanation)
    print("=" * width + "\n")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        An argparse.Namespace object containing the arguments
    """
    parser = argparse.ArgumentParser(
        description="AI-Enhanced IP Subnet Calculator Assistant",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # Explain concept
    explain_parser = subparsers.add_parser('explain', help='Get an explanation of a subnetting concept')
    explain_parser.add_argument('concept', help='Concept to explain (e.g., "CIDR notation", "VLSM", "supernetting")')
    
    # Plan network
    plan_parser = subparsers.add_parser('plan', help='Generate a network plan based on requirements')
    plan_parser.add_argument('requirements', help='Description of network requirements')
    
    # Solve problem
    solve_parser = subparsers.add_parser('solve', help='Get help solving a subnetting problem')
    solve_parser.add_argument('problem', help='Description of the problem to solve')
    
    # Generate quiz
    quiz_parser = subparsers.add_parser('quiz', help='Generate a subnetting quiz question')
    quiz_parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'], default='medium', 
                          help='Difficulty level (default: medium)')
    
    # Troubleshoot issue
    troubleshoot_parser = subparsers.add_parser('troubleshoot', help='Get troubleshooting guidance')
    troubleshoot_parser.add_argument('issue', help='Description of the networking issue')
    
    # Interactive mode
    subparsers.add_parser('interactive', help='Enter interactive mode')
    
    return parser.parse_args()


def interactive_mode(subnet_ai: SubnetAI) -> None:
    """
    Run the AI assistant in interactive mode.
    
    Args:
        subnet_ai: SubnetAI instance
    """
    print("\n" + "=" * 50)
    print("AI-Enhanced IP Subnet Calculator - Interactive Mode")
    print("=" * 50 + "\n")
    
    while True:
        print("Available operations:")
        print("1. Explain a subnetting concept")
        print("2. Plan a network")
        print("3. Get help with a subnetting problem")
        print("4. Generate a practice quiz question")
        print("5. Troubleshoot a networking issue")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            concept = input("Enter the subnetting concept you want explained: ").strip()
            explanation = subnet_ai.explain_subnetting_concept(concept)
            display_explanation(explanation)
            
        elif choice == '2':
            requirements = input("Describe your network requirements: ").strip()
            plan = subnet_ai.plan_network(requirements)
            display_explanation(plan)
            
        elif choice == '3':
            problem = input("Describe the subnetting problem you need help with: ").strip()
            solution = subnet_ai.analyze_subnet_problem(problem)
            display_explanation(solution)
            
        elif choice == '4':
            difficulties = {'1': 'easy', '2': 'medium', '3': 'hard'}
            diff_choice = input("Select difficulty (1=Easy, 2=Medium, 3=Hard): ").strip()
            difficulty = difficulties.get(diff_choice, 'medium')
            
            quiz = subnet_ai.get_quiz_question(difficulty)
            print("\n" + "=" * 80)
            print("QUESTION:")
            print(quiz["question"])
            print("\n" + "-" * 40)
            
            # Prompt for answer attempt
            input("Press Enter when you're ready to see the answer...")
            
            print("\nANSWER:")
            print(quiz["answer"])
            print("\nEXPLANATION:")
            print(quiz["explanation"])
            print("=" * 80 + "\n")
            
        elif choice == '5':
            issue = input("Describe the networking issue you're experiencing: ").strip()
            guidance = subnet_ai.troubleshoot_subnet_issue(issue)
            display_explanation(guidance)
            
        elif choice == '6':
            print("\nExiting AI Subnet Assistant. Goodbye!\n")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")
        
        print()  # Extra line for readability


def main() -> int:
    """
    Main function to run the AI subnet assistant.
    
    Returns:
        Exit code
    """
    try:
        args = parse_arguments()
        subnet_ai = SubnetAI()
        
        if args.mode == 'explain':
            explanation = subnet_ai.explain_subnetting_concept(args.concept)
            display_explanation(explanation)
            
        elif args.mode == 'plan':
            plan = subnet_ai.plan_network(args.requirements)
            display_explanation(plan)
            
        elif args.mode == 'solve':
            solution = subnet_ai.analyze_subnet_problem(args.problem)
            display_explanation(solution)
            
        elif args.mode == 'quiz':
            quiz = subnet_ai.get_quiz_question(args.difficulty)
            print("\nQUESTION:")
            print(quiz["question"])
            print("\n" + "-" * 40)
            
            # Prompt for answer attempt
            input("Press Enter when you're ready to see the answer...")
            
            print("\nANSWER:")
            print(quiz["answer"])
            print("\nEXPLANATION:")
            print(quiz["explanation"])
            
        elif args.mode == 'troubleshoot':
            guidance = subnet_ai.troubleshoot_subnet_issue(args.issue)
            display_explanation(guidance)
            
        elif args.mode == 'interactive' or args.mode is None:
            interactive_mode(subnet_ai)
            
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
