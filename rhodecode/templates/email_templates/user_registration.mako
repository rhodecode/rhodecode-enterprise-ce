## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
RhodeCode new user registration: ${user.username}
</%def>

<%def name="body_plaintext()" filter="n,trim">

A new user `${user.username}` has registered on ${h.format_date(date)}

- Username: ${user.username}
- Full Name: ${user.firstname} ${user.lastname}
- Email: ${user.email}
- Profile link: ${h.url('user_profile', username=user.username, qualified=True)}

${self.plaintext_footer()}
</%def>

## BODY GOES BELOW
<table style="text-align:left;vertical-align:middle;">
    <tr><td colspan="2" style="width:100%;padding-bottom:15px;border-bottom:1px solid #dbd9da;"><h4><a href="${h.url('user_profile', username=user.username, qualified=True)}" style="color:#427cc9;text-decoration:none;cursor:pointer">${_('New user %(user)s has registered on %(date)s') % {'user': user.username, 'date': h.format_date(date)}}</h4></td></tr>
    <tr><td style="padding-right:20px;padding-top:20px;">${_('Username')}</td><td style="line-height:1;padding-top:20px;"><img style="margin-bottom:-5px;text-align:left;border:1px solid #dbd9da" src="${h.gravatar_url(user.email, 16)}" height="16" width="16">&nbsp;${user.username}</td></tr>
    <tr><td style="padding-right:20px;">${_('Full Name')}</td><td>${user.firstname} ${user.lastname}</td></tr>
    <tr><td style="padding-right:20px;">${_('Email')}</td><td>${user.email}</td></tr>
    <tr><td style="padding-right:20px;">${_('Profile')}</td><td><a href="${h.url('user_profile', username=user.username, qualified=True)}">${h.url('user_profile', username=user.username, qualified=True)}</a></td></tr>
</table>