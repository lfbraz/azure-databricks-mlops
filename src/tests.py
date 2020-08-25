# Databricks notebook source
import unittest
from pytest_databricks.helper import run_unittest

class TestMyApp(unittest.TestCase):
    
  def test_1_notequal_2(self):
    self.assertNotEqual(1, 2)
    
test_result = run_unittest(TestMyApp)
print(test_result['run_output'])