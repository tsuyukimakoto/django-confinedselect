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
from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils import simplejson

class ConfinedSelect(forms.Select):
  def __init__(self, rel, attrs=None, choices=(), parent_field_name=None):
    self.rel = rel
    self.parent_field_name = parent_field_name
    super(ConfinedSelect, self).__init__(attrs, choices)

  def render(self, name, value, attrs=None):
    if attrs is None:
      attrs = {}
    if not attrs.has_key('class'):
      attrs['class'] = 'vConfinedSelect'
    output = [super(ConfinedSelect, self).render(name, value, attrs)]
    # TODO: "id_" is hard-coded here. This should instead use the correct
    # API to determine the ID dynamically.
    output.append(u'''<script type="text/javascript">
    %(parent_field_name)s_%(child_field_name)s_confine_choices = function() {
      p = document.getElementById('id_%(parent_field_name)s');
      c = document.getElementById("id_%(child_field_name)s");
      id_%(child_field_name)s_before = (c.selectedIndex > -1) ? c.options[c.selectedIndex].value : "";
      c.selectedIndex = null;
      while(c.length > 0) {
        c.remove(c.length - 1);
      }
      xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState==4) {
          var res = eval(xmlhttp.responseText);
          for(var i=0;i < res.length;i++) {
            var opt = document.createElement("option");
            opt.value = res[i].id;
            opt.text = res[i].data;
            try {
              c.add(opt, null);
            }catch(e){
              c.add(opt);
            }
            if(opt.value == id_%(child_field_name)s_before) c.selectedIndex = i;
          }
          if(document.all) c.fireEvent("onchange");
          else {
            var ev = document.createEvent("HTMLEvents");
            ev.initEvent('change', true, false);
            c.dispatchEvent(ev);
          }
        }
      };
      xmlhttp.open( 'GET' , '../search/?parent_id=' + p.options[p.selectedIndex].value + '&app_label=%(app_label)s&model_name=%(model_name)s&parent_field_name=%(parent_field_name)s' , false );
      xmlhttp.send();
    };

    var elm = document.getElementById('id_%(parent_field_name)s');
    addEvent(elm,'change',%(parent_field_name)s_%(child_field_name)s_confine_choices,false);
    %(parent_field_name)s_%(child_field_name)s_confine_choices();
    </script>
    ''' % dict(parent_field_name=self.parent_field_name, child_field_name=name, app_label=self.rel.to._meta.app_label, model_name=self.rel.to._meta.module_name))
    return mark_safe(u''.join(output))

class RefinedAdmin(admin.ModelAdmin):
  filiations = ()

  def ajax_search(self, request):
    query = request.GET.get('parent_id', None)
    app_label = request.GET.get('app_label', None)
    model_name = request.GET.get('model_name', None)
    parent_field_name = request.GET.get('parent_field_name', None)
    if parent_field_name and app_label and model_name and query:
      model = models.get_model(app_label, model_name)
      query_dict = {str(parent_field_name):query}
      qs = model._default_manager.filter(**query_dict)
      responsedata = '{%s}' % (simplejson.dumps([dict(id=data.id, data=force_unicode(data)) for data in qs]))
      return HttpResponse(responsedata, mimetype="application/javascript")
    return HttpResponse('{[]}', mimetype="application/javascript")

  def __call__(self, request, url):
    if url is None:
      pass
    elif url == 'search':
      return self.ajax_search(request)
    return super(RefinedAdmin, self).__call__(request, url)

  def formfield_for_dbfield(self, db_field, **kwargs):
    if isinstance(db_field, models.ForeignKey):
      filiation = [p for p in self.filiations if p[1] == db_field.name]
      if filiation:
        filiation = filiation[0]
        kwargs['widget'] = ConfinedSelect(db_field.rel, parent_field_name=filiation[0])
    return super(RefinedAdmin, self).formfield_for_dbfield(db_field, **kwargs)
