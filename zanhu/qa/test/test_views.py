#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'


import json
from django.test import RequestFactory
from test_plus.test import CBVTestCase
from django.contrib.messages.storage.fallback import FallbackStorage

from zanhu.qa.models import Question, Answer
from zanhu.qa import views


class BaseQATestCase(CBVTestCase):
    """测试基类"""
    def setUp(self):
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")

        self.first_question = Question.objects.create(
            title="问题1",
            content="问题1的描述",
            user=self.user,
            tags="test1, test2",
        )

        self.second_question = Question.objects.create(
            title="问题2",
            content="问题2的描述",
            user=self.user,
            tags="test1",
            has_answer=True
        )

        self.answer = Answer.objects.create(
            content="问题2的回答",
            user=self.other_user,
            question=self.second_question,
            is_answer=True,
        )

        self.request = RequestFactory().get("/fake-url/")
        # 使用RequestFactory创建请求，get后面的url可以是任意的，因为请求不会经过url匹配
        # 这个request对象相当于模拟浏览器发出的get请求
        self.request.user = self.user   # 给request对象添加user表示用户登录信息


class TestQuestionListView(BaseQATestCase):
    """测试问题列表"""
    def test_context_data(self):
        response = self.get(views.QuestionListView, request=self.request)
        # 使用基类中的request向views.QuestionListView视图发送get请求

        self.assertEqual(response.status_code, 200)

        # 判断查询集里的所有数据是否一致         方式1
        self.assertQuerysetEqual(
            qs=response.context_data["questions"],
            # values=[repr(self.first_question), repr(self.second_question)],
            values=map(repr, [self.first_question, self.second_question]),
            ordered=False,
        )

        # 直接遍历循环判断查询集的每一个数据      方式2
        self.assertTrue(all(a == b for a, b in zip(Question.objects.all(), response.context_data["questions"])))
        # 使用zip将查询集和response中的questions进行组合，得到每一个对象对应的前端查询集对象，使用for循环遍历每一个元组赋给a，b
        # 使用all()判断a，b是否一致

        # 判断上下文参数
        self.assertContext("active", "all")
        self.assertContext("popular_tags", Question.objects.get_counted_tags())


class TestAnsweredListView(BaseQATestCase):
    def test_context_data(self):
        # 获取返回的响应对象
        # response = self.get(views.AnsweredListView, request=self.request)  # 方式1
        response = views.AnsweredListView.as_view()(self.request)          # 方式2  将request传递给as_view得到的response
        assert response.status_code == 200

        self.assertQuerysetEqual(response.context_data["questions"],[repr(self.second_question)])

        # self.assertContext("active", "answered")  # 对应方式1
        self.assertEqual(response.context_data["active"], "answered")   # 对应方式2


class TestUnAnsweredListView(BaseQATestCase):
    def test_context_data(self):
        response = self.get(
            views.UnAnsweredListView,
            request=self.request,
        )
        assert response.status_code == 200
        self.assertQuerysetEqual(response.context_data["questions"], [repr(self.first_question)])
        self.assertContext("active", "unanswered")


class TestCreateQuestionView(BaseQATestCase):
    def test_get(self):
        response = self.get(views.CreateQuestionView, request=self.request)
        assert response.status_code == 200

        # 判断响应体的文本内容是否包含对应文字
        self.assertContains(response, "问题标题")
        self.assertContains(response, "问题内容")
        self.assertContains(response, "问题标签")
        self.assertContains(response, "编辑")
        self.assertContains(response, "预览")

        # 判断响应结果内的视图对象是否是视图类的实例对象
        self.assertIsInstance(response.context_data["view"], views.CreateQuestionView)

    def test_post(self):
        data = {"title": "title", "content": "content", "tags": "tag1, tag2", "status": "O"}
        request = RequestFactory().post("/fake-url/", data=data)
        request.user = self.user
        # RequestFactory测试含有django.contrib.messages的视图 https://code.djangoproject.com/ticket/17971
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.CreateQuestionView, request=request)
        assert response.status_code == 302
        assert response.url == '/qa/indexed/'


class TestQuestionDetailView(BaseQATestCase):
    def test_get_context_data(self):
        response = self.get(views.DetailQuestionView, request=self.request, pk=self.first_question.id)
        self.response_200(response)
        self.assertEqual(response.context_data["question"], self.first_question)


class TestCreateAnswerView(BaseQATestCase):
    def test_get(self):
        response = self.get(views.CreateAnswerView, request=self.request, question_id=self.first_question.id)
        self.response_200(response)

        self.assertContains(response, "回答内容")
        self.assertContains(response, "编辑")
        self.assertContains(response, "预览")

        self.assertIsInstance(response.context_data["view"], views.CreateAnswerView)

    def test_post(self):
        request = RequestFactory().post("/fake-url/", data={"content": "新回答"})
        request.user = self.other_user
        # RequestFactory测试含有django.contrib.messages的视图 https://code.djangoproject.com/ticket/17971
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.CreateAnswerView, request=request, question_id=self.first_question.id)
        self.response_302(response)
        self.assertEqual(response.url, f"/qa/question-detail/{self.first_question.id}/")


# class TestUpdateAnswerView(BaseQATestCase):
#     def test_get(self):
#         response = self.get(views.UpDateAnswerView, request=self.request)
#         assert response.status == 200
#
#         self.assertContains(response, "回答内容")
#         self.assertContains(response, "提交编辑")
#         self.assertIsInstance(response.context_data["view"], views.UpDateAnswerView)
#
#     def test_post(self):
#         pass


class TestQAvote(BaseQATestCase):
    def setUp(self):
        # 将基类的初始化数据拿来使用
        super(TestQAvote, self).setUp()
        self.request = RequestFactory().post("/fake-url/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        # QueryDict instance is immutable, request.POST是QueryDict对象，不可变
        self.request.POST = self.request.POST.copy()
        self.request.user = self.other_user


    def test_upvote_question(self):
        self.request.POST["question"] = self.first_question.id
        self.request.POST["value"] = "U"
        response = views.question_vote(self.request)
        self.response_200(response)
        self.assertEqual(json.loads(response.content)["votes"], 1)

    def test_downvote_question(self):
        self.request.POST["question"] = self.first_question.id
        self.request.POST["value"] = "D"
        response = views.question_vote(self.request)
        self.response_200(response)
        self.assertEqual(json.loads(response.content)["votes"], -1)

    def test_upvote_answer(self):
        self.request.POST["answer"] = self.answer.uuid
        self.request.POST["value"] = "U"
        response = views.answer_vote(self.request)
        self.response_200(response)
        self.assertEqual(json.loads(response.content)["votes"], 1)

    def test_downvote_answer(self):
        self.request.POST["answer"] = self.answer.uuid
        self.request.POST["value"] = "D"
        response = views.answer_vote(self.request)
        self.response_200(response)
        self.assertEqual(json.loads(response.content)["votes"], -1)

    def test_accept_answer(self):
        self.request.user = self.user  # 视图中对用户做了判断，所以要给request传递一个提问者的用户信息
        self.request.POST["answer"] = self.answer.uuid
        response = views.accept_answer(self.request)
        self.response_200(response)
        self.assertEqual(json.loads(response.content)["status"], "true")


"""
from test_plus.test import TestCase
from django.test import Client
from django.urls import reverse
from zanhu.qa.models import Question, Answer


class QAViewsTest(TestCase):
    def setUp(self) -> None:
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")

        self.client = Client()
        self.other_client = Client()

        self.client.login(username="user01", password="password")
        self.other_client.login(username="user02", password="password")

        self.first_question = Question.objects.create(
            title="问题1",
            content="问题1的描述",
            user=self.user,
            tags="test1, test2",
        )

        self.second_question = Question.objects.create(
            title="问题2",
            content="问题2的描述",
            user=self.user,
            tags="test1",
            has_answer=True
        )

        self.answer = Answer.objects.create(
            content="问题2的回答",
            user=self.other_user,
            question=self.second_question,
            is_answer=True,
        )

    def test_all_questions(self):
        response = self.client.get(reverse("qa:all_q"))
        assert response.status_code == 200
        assert self.first_question in response.context["questions"]
        assert self.second_question in response.context["questions"]
        assert "问题2" == str(response.context["questions"][0])  # 模型类的排序是按创建时间倒叙 所以问题2在第一个位置 即索引0

    def test_answered_question(self):
        response = self.client.get(reverse("qa:answered_q"))
        assert response.status_code == 200
        assert self.second_question in response.context["questions"]

    def test_unanswered_question(self):
        response = self.client.get(reverse("qa:unanswered_q"))
        assert response.status_code == 200
        assert self.first_question in response.context["questions"]

    def test_create_question(self):
        response = self.client.post(
            reverse("qa:ask_question"),
            {
                "title": "问题3",
                "content": "问题3的描述",
                "user": self.user,
                "tags": "test3",
                "status": "O",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 3)
        self.assertEqual(str(Question.objects.first()), "问题3")

    def test_answer_question(self):
        response = self.other_client.post(
            reverse("qa:propose_answer", kwargs={"question_id": self.first_question.pk}),
            {
                "content": "问题1的回答",
                "question": self.first_question,
                "user": self.other_user,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Answer.objects.count(), 2)

    def test_upvote_question(self):
        response = self.other_client.post(
            reverse("qa:question_vote"),
            {
                "value": "U",
                "question": self.first_question.pk,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        assert response.status_code == 200


    def test_downvote_question(self):
        response = self.other_client.post(
            reverse("qa:question_vote"),
            {
                "value": "D",
                "question": self.first_question.pk,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code == 200
"""
