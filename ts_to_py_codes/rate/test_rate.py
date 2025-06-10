import unittest
from rate import evaluate_snippet

class TestSnippetEvaluator(unittest.TestCase):
    def test_hardware_query(self):
        context = """Resource: https://brain.overment.com/
Title: brain.overment.com | brain.overment.com
Snippet: The most important thing to me is performance of the hardware, minimalistic design and my workflow. This is possible thanks to many Apps which are available on macOS / iOS only."""
        query = "List Hardware mentioned on this page https://brain.overment.com/"
        
        result = evaluate_snippet(context, query)
        
        self.assertIsInstance(result, dict)
        self.assertIn('reason', result)
        self.assertIn('score', result)
        self.assertIsInstance(result['reason'], str)
        self.assertIsInstance(result['score'], (int, float))
        self.assertTrue(0 <= result['score'] <= 0.5)
        self.assertIn('hardware', result['reason'].lower())

    def test_apps_query(self):
        context = """Resource: https://brain.overment.com/
Title: Apps | brain.overment.com
Snippet: This is the latest (Q2 2024) list of apps I use: Arc — The best web browser I know. Alice — OpenAI / Anthropic / Ollama desktop experience. iA Writer — My favorite text editor Kindle, Audible, & Goodreads — Apps for reading & listening Raycast — Advanced launcher for macOS Linear — Project management app I use for self-management."""
        query = "List Hardware mentioned on this page https://brain.overment.com/"
        
        result = evaluate_snippet(context, query)
        
        self.assertIsInstance(result, dict)
        self.assertIn('reason', result)
        self.assertIn('score', result)
        self.assertIsInstance(result['reason'], str)
        self.assertIsInstance(result['score'], (int, float))
        self.assertTrue(0.1 <= result['score'] <= 0.4)
        self.assertTrue(
            'apps' in result['reason'].lower() or 
            'software' in result['reason'].lower()
        )

    def test_ted_talk_query(self):
        context = """Resource: https://youtube.com
Title: How to Think Computationally About AI, the Universe and Everything | Stephen Wolfram | TED
Link: https://www.youtube.com/watch?v=fLMZAHyrpyo
Snippet: Drawing on his decades-long mission to formulate the world in computational terms, Stephen Wolfram delivers a profound vision of computation and its role in ..."""
        query = "Find me Stephen Wolfram latest TED talk on youtube"
        
        result = evaluate_snippet(context, query)
        
        self.assertIsInstance(result, dict)
        self.assertIn('reason', result)
        self.assertIn('score', result)
        self.assertIsInstance(result['reason'], str)
        self.assertIsInstance(result['score'], (int, float))
        self.assertTrue(0.9 <= result['score'] <= 1.0)
        self.assertIn('wolfram', result['reason'].lower())
        self.assertIn('ted', result['reason'].lower())

if __name__ == '__main__':
    unittest.main() 