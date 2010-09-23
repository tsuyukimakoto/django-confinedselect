# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 Makoto Tsuyuki All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#  3. Neither the name of the authors nor the names of its contributors
#     may be used to endorse or promote products derived from this
#     software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from django.db import models

class MasterA(models.Model):
  name = models.CharField(max_length=20)

  def __unicode__(self):
    return self.name

class MasterB(models.Model):
  name = models.CharField(max_length=20)
  master_a = models.ForeignKey(MasterA)

  def __unicode__(self):
    return self.name

class MasterC(models.Model):
  name = models.CharField(max_length=20)
  master_b = models.ForeignKey(MasterB)

  def __unicode__(self):
    return self.name

class SampleModel(models.Model):
  name = models.CharField(max_length=20)
  master_a = models.ForeignKey(MasterA)
  master_b = models.ForeignKey(MasterB)
  master_c = models.ForeignKey(MasterC)

  def __unicode__(self):
      return self.name
