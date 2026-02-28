import unittest
import app


class TestChecks(unittest.TestCase):
    def test_app(self):
        res = app.lambda_handler()
        self.assertIsInstance(res, dict)
        self.assertEqual(res, {
            'statusCode': 200,
            'body': f"Hello World!"
        })


if __name__ == "__main__":
    unittest.main()
