## -*- coding: utf-8 -*-

## headers we additionally can set for email
<%def name="headers()" filter="n,trim"></%def>

<%def name="plaintext_footer()">
${_('This is a notification from RhodeCode. %(instance_url)s') % {'instance_url': instance_url}}
</%def>

<%def name="body_plaintext()" filter="n,trim">
## this example is not called itself but overridden in each template
## the plaintext_footer should be at the bottom of both html and text emails
${self.plaintext_footer()}
</%def>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>${self.subject()}</title>
    <style type="text/css">
        /* Based on The MailChimp Reset INLINE: Yes. */  
        #outlook a {padding:0;} /* Force Outlook to provide a "view in browser" menu link. */
        body{width:100% !important; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; margin:0; padding:0;} 
        /* Prevent Webkit and Windows Mobile platforms from changing default font sizes.*/ 
        .ExternalClass {width:100%;} /* Force Hotmail to display emails at full width */  
        .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div {line-height: 100%;}
        /* Forces Hotmail to display normal line spacing.  More on that: http://www.emailonacid.com/forum/viewthread/43/ */ 
        #backgroundTable {margin:0; padding:0; line-height: 100% !important;}
        /* End reset */

        /* defaults for images*/
        img {outline:none; text-decoration:none; -ms-interpolation-mode: bicubic;} 
        a img {border:none;} 
        .image_fix {display:block;}

        body {line-height:1.2em;}
        p {margin: 0 0 20px;}
        h1, h2, h3, h4, h5, h6 {color:#323232!important;}
        a {color:#427cc9;text-decoration:none;outline:none;cursor:pointer;}
        a:focus {outline:none;}
        a:hover {color: #305b91;}
        h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {color:#427cc9!important;text-decoration:none!important;}
        h1 a:active, h2 a:active,  h3 a:active, h4 a:active, h5 a:active, h6 a:active {color: #305b91!important;}
        h1 a:visited, h2 a:visited,  h3 a:visited, h4 a:visited, h5 a:visited, h6 a:visited {color: #305b91!important;}
        table {font-size:13px;border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt;}
        table td {padding:.65em 1em .65em 0;border-collapse:collapse;vertical-align:top;text-align:left;}
        input {display:inline;border-radius:2px;border-style:solid;border: 1px solid #dbd9da;padding:.5em;}
        input:focus {outline: 1px solid #979797}
        @media only screen and (-webkit-min-device-pixel-ratio: 2) {
        /* Put your iPhone 4g styles in here */ 
        }

        /* Android targeting */
        @media only screen and (-webkit-device-pixel-ratio:.75){
        /* Put CSS for low density (ldpi) Android layouts in here */
        }
        @media only screen and (-webkit-device-pixel-ratio:1){
        /* Put CSS for medium density (mdpi) Android layouts in here */
        }
        @media only screen and (-webkit-device-pixel-ratio:1.5){
        /* Put CSS for high density (hdpi) Android layouts in here */
        }
        /* end Android targeting */

    </style>

    <!-- Targeting Windows Mobile -->
    <!--[if IEMobile 7]>
    <style type="text/css">
    
    </style>
    <![endif]-->

    <!--[if gte mso 9]>
        <style>
        /* Target Outlook 2007 and 2010 */
        </style>
    <![endif]-->
</head>
<body>
<!-- Wrapper/Container Table: Use a wrapper table to control the width and the background color consistently of your email. Use this approach instead of setting attributes on the body tag. -->
<table cellpadding="0" cellspacing="0" border="0" id="backgroundTable" align="left" style="margin:1%;width:97%;padding:0;font-family:sans-serif;font-weight:100;border:1px solid #dbd9da">
    <tr>
        <td valign="top" style="padding:0;"> 
            <table cellpadding="0" cellspacing="0" border="0" align="left" width="100%">
                <tr><td style="width:100%;padding:7px;background-color:#202020" valign="top">
                    <a style="width:100%;height:100%;display:block;color:#eeeeee;text-decoration:none;" href="${instance_url}">
                        ${_('RhodeCode')}
                        % if rhodecode_instance_name:
                            - ${rhodecode_instance_name}
                        % endif
                    </a>
                </td></tr>
                <tr><td style="padding:15px;" valign="top">${self.body()}</td></tr>
            </table>
        </td>
    </tr>
</table>  
<!-- End of wrapper table -->
<p><a style="margin-top:15px;margin-left:1%;font-family:sans-serif;font-weight:100;font-size:11px;display:block;color:#666666;text-decoration:none;" href="${instance_url}">
    ${self.plaintext_footer()}
</a></p>
</body>
</html>
