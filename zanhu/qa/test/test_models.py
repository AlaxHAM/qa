#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from test_plus.test import TestCase
from zanhu.qa.models import Question, Answer


class ArticleModelsTest(TestCase):
    """文章模型类测试"""

    def setUp(self) -> None:
        """初始化操作"""
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")

        self.first_question = Question.objects.create(
            title="问题1",
            content="问题1的内容",
            user=self.user,
            tags="测试1, 测试2"
        )

        self.second_question = Question.objects.create(
            title="问题2",
            content="问题2的内容",
            user=self.user,
            has_answer=True,
            tags="测试1, 测试2"
        )

        self.first_answer = Answer.objects.create(
            content="问题1的答案",
            user=self.user,
            question=self.second_question,
            is_answer=True,
        )

    def test_vote_question(self):
        """测试对问题投票"""
        self.first_question.votes.update_or_create(user=self.user, defaults={"value": True})
        self.first_question.votes.update_or_create(user=self.other_user, defaults={"value": True})
        assert self.first_question.total_votes() == 2

    def test_vote_answer(self):
        """对回答投票"""
        self.first_answer.votes.update_or_create(user=self.user, defaults={"value": True})
        self.first_answer.votes.update_or_create(user=self.other_user, defaults={"value": False})
        assert self.first_answer.total_votes() == 0

    def test_get_question_voter(self):
        """获取对问题投票的用户"""
        self.first_question.votes.update_or_create(user=self.user, defaults={"value": True})
        self.first_question.votes.update_or_create(user=self.other_user, defaults={"value": False})
        assert self.user in self.first_question.get_upvoters()
        assert self.other_user in self.first_question.get_downvoters()

    def test_get_answer_voter(self):
        """获取对回答投票的用户"""
        self.first_answer.votes.update_or_create(user=self.user, defaults={"value": True})
        self.first_answer.votes.update_or_create(user=self.other_user, defaults={"value": False})
        assert self.user in self.first_answer.get_upvoters()
        assert self.other_user in self.first_answer.get_downvoters()

    def test_unanswered_question(self):
        """未被回答的问题"""
        assert self.first_question == Question.objects.get_unanswered()[0]

    def test_answered_question(self):
        """已被回答的问题"""
        assert self.second_question == Question.objects.get_answered()[0]

    def test_all_question(self):
        """获取问题的所有回答"""
        assert self.first_answer == self.second_question.get_answers()[0]
        assert self.second_question.count_answer() == 1

    def test_question_accepted_answer(self):
        """提问者接受回答"""
        first_answer = Answer.objects.create(
            content="回答1",
            user=self.user,
            question=self.first_question,
        )

        second_answer = Answer.objects.create(
            content="回答2",
            user=self.user,
            question=self.first_question,
        )

        third_answer = Answer.objects.create(
            content="回答3",
            user=self.other_user,
            question=self.first_question,
        )

        self.assertFalse(first_answer.is_answer)   # 判断是否是被接受的回答，默认创建时is_answer是false，assertFalse判断是否是False
        self.assertFalse(second_answer.is_answer)
        self.assertFalse(third_answer.is_answer)

        # 将 回答3 改为接受的回答
        third_answer.accept_answer()

        self.assertFalse(first_answer.is_answer)
        self.assertFalse(second_answer.is_answer)
        self.assertTrue(third_answer.is_answer)   # 判断是否为True

    def test_question_str_(self):
        assert isinstance(self.first_question, Question)
        assert str(self.first_question) == "问题1"

    def test_answer_str_(self):
        assert isinstance(self.first_answer, Answer)
        assert str(self.first_answer) == "问题1的答案"
