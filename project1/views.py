from django.shortcuts import render
#import request
from django.http import HttpResponse


def test(rq):

    return HttpResponse("Success")