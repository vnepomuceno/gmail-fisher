from typing import Iterable

import pytest as pytest

from gmail_fisher.models import GmailMessage


@pytest.fixture
def bolt_email_html_body() -> str:
    return """<!DOCTYPE HTML>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0">
    <meta name="x-apple-disable-message-reformatting"/>
    <meta content="telephone=no" name="format-detection"/>
    <!--[if !mso]><!-->
    <meta http-equiv="X-UA-Compatible" content="IE=Edge"><!--<![endif]-->
    <!--[if (gte mso 9)|(IE)]>
    <xml>
        <o:OfficeDocumentSettings>
            <o:AllowPNG/>
            <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
    </xml>
    <![endif]-->
    <!--[if (gte mso 9)|(IE)]>
    <style type="text/css">
        body {
            width: 600px;
            margin: 0 auto;
        }

        table {
            border-collapse: collapse;
        }

        table, td {
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }

        img {
            -ms-interpolation-mode: bicubic;
        }
    </style>
    <![endif]-->
    <style type="text/css">
        a {
            text-decoration: none;
            color: #7C7D86;
        }

        .ii a[href] {
            color: #7C7D86;
        }

        .address-title {
            color: #7C7D86 !important;
            text-decoration: none !important;
        }

        .order-date {
            text-decoration: none;
            color: #7C7D86;
        }

        u + #body a {
            color: inherit;
            text-decoration: none;
            font-size: inherit;
            font-family: inherit;
            font-weight: inherit;
            line-height: inherit;
        }

        a[x-apple-data-detectors] {
            color: inherit !important;
            text-decoration: none !important;
            font-size: inherit !important;
            font-family: inherit !important;
            font-weight: inherit !important;
            line-height: inherit !important;
        }

        @media only screen and (max-width: 480px) {
            .under-footer {
                background-color: #FFFFFF !important;
                background: #FFFFFF !important;
            }

            .v-divider,
            .footer-divider {
                background-color: #FFFFFF !important;
                background: #FFFFFF !important;
            }

            .footer-divider {
                display: none;
            }

            .left-button,
            .right-button,
            .btn-wrap {
                background-color: #F4F4F6 !important;
                background: #F4F4F6 !important;
            }

            .title-photo {
                width: 101px;
                height: 105px;
            }

            .title-photo-block {
                height: 53px !important;
            }

            .header {
                margin-top: 32px !important;
            }

            .header-label {
                padding-top: 4px !important;
            }

            .arrow-down {
                padding-bottom: 12px;
            }

            u ~ div {
                min-width: 100%;
            }

        }
    </style>
</head>

<body style="color: #2F313F; font-family: 'Google Sans', Helvetica, Arial; font-size: 16px; margin: 0 !important; width: 100%; width: 100%; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; -webkit-font-smoothing: subpixel-antialiased; -webkit-backface-visibility: hidden; -moz-backface-visibility: hidden; -ms-backface-visibility: hidden; -ms-text-size-adjust: 100%; -moz-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; text-rendering: geometricPrecision;"
      class="body">
<center class="wrapper" data-link-color="#1188E6" data-body-style="font-size: 14px; font-family: arial; color: #000000; background-color: #f4f4f6;">
    <div class="webkit" style="font-family: 'Google Sans', Helvetica, Arial; font-size: 16px;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%" class="wrapper" bgcolor="#FFFFFF"
               style="-moz-text-size-adjust: 100%; -ms-text-size-adjust: 100%; -webkit-font-smoothing: antialiased; -webkit-text-size-adjust: 100%; table-layout: fixed; width: 100%; width: 100%;">
            <tr>
                <td style="padding: 0;">
                    <table cellpadding="0" cellspacing="0" style="margin: 0 auto;width: 100%; border-collapse:collapse; background: #F4F4F6;" bgcolor="#F4F4F6" class="header">
                        <tr>
                            <td>
                                <table cellpadding="0" cellspacing="0" style="margin: 0 auto;max-width:632px; width: 100%; border-collapse:collapse;">
                                    <tr>
                                        <td colspan="2" style="padding: 40px 0 0 16px;vertical-align: top" class="logo-wrap">
                                            <img src="https://taxify-static-content-for-public-web.s3.eu-central-1.amazonaws.com/invoicing/email_resource/delivery/BoltFood.png" alt width="141" height="34">
                                        </td>
                                        <td style="vertical-align: top; text-align: right; padding-right: 16px; padding-top: 40px;">
                                            <span class="order-date"
                                                  style="margin: 0;font-size: 14px; line-height: 18px; color: #7C7D86 !important; font-family: 'Google Sans', Helvetica, Arial; text-decoration: none; pointer-events: none; display: block;">&#173;07-11-2021</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td colspan="2" style="padding: 20px 10px 31px 16px;">
                                            <p style="margin: 0 0 9px;color: #2f313f; font-size: 24px; line-height: 30px; font-weight: bold !important; font-family: 'Google Sans', Helvetica, Arial;"><b>Bon Appetit,<br> Valter!</b></p>
                                            <p style="margin: 0;color: #7C7D86; font-size: 16px; line-height: 20px; font-family: 'Google Sans', Helvetica, Arial;">This is your receipt.</p>
                                        </td>
                                        <td style="padding-right: 24px; text-align: right; padding-top: 35px; padding-bottom: 31px; vertical-align: bottom;" class="title-photo-wrap">
                                            <div style="display: block; height: 53px;" class="title-photo-block">
                                                <img class="title-photo" style="width: 116px; height: 120px; margin-left: auto; margin-right: 0; display: block;"
                                                     srcset="https://taxify-static-content-for-public-web.s3.eu-central-1.amazonaws.com/invoicing/email_resource/delivery/Illustration.png 2x"
                                                     src="https://taxify-static-content-for-public-web.s3.eu-central-1.amazonaws.com/invoicing/email_resource/delivery/Illustration.png" alt width="116" height="120" align="top"/>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    <table cellpadding="0" cellspacing="0" style="margin: 0 auto;max-width:632px; width: 100%; border-collapse:collapse;">
                        <tr>
                            <td colspan="3" class="header-wrapper" style="background: #FFFFFF;padding: 0;">
                                <table class="header" width="100%" cellpadding="0" cellspacing="0" style="border: none; border-collapse: collapse; width: 100%; margin-bottom: 30px;">
                                    <tr>
                                        <td class="header-label" style="padding: 40px 16px 0;">
                                            <div style="margin: 0 auto;max-width: 600px; width: 100%;">
                                                <span style="display: block; margin-top: 0; margin-bottom: 0; color: #7C7D86; font-size: 14px; line-height: 16px; font-family: 'Google Sans', Helvetica, Arial;">From</span>
                                                <span style="display: block; margin-top: 4px; margin-bottom: 5px; color: #2f313f; font-size: 20px;line-height: 24px; font-family: 'Google Sans', Helvetica, Arial;">Hello Beijing</span>
                                                <a href=""
                                                   style="display: block; margin-top: 0; margin-bottom: 0; color: #7C7D86 !important; font-size: 14px; line-height: 16px; font-family: 'Google Sans', Helvetica, Arial; text-decoration: none; !important; cursor: default;"
                                                   class="address-title" x-apple-data-detectors="true">&#173;Av. Da República, 97 B - Lisboa 1050-197</a>
                                            </div>
                                        </td>
                                    </tr>

                                    <tr>
                                        <td style="padding: 0 16px;">
                                            <div style="margin-left: auto; margin-right: auto; max-width: 600px; width: 100%;     padding-top: 15px;" class="arrow-down">
                                                <img style="width: 24px; height: 24px;" srcset="https://taxify-static-content-for-public-web.s3.eu-central-1.amazonaws.com/invoicing/email_resource/delivery/ic_arrow_right.png 2x"
                                                     src="https://taxify-static-content-for-public-web.s3.eu-central-1.amazonaws.com/invoicing/email_resource/delivery/ic_arrow_right.png" alt="" width="24" height="24">
                                            </div>
                                        </td>
                                    </tr>

                                    <tr>
                                        <td class="header-label" style="padding: 16px 16px 27px;">
                                            <div style="margin: 0 auto;max-width: 600px; width: 100%;">
                                                <span style="display: block; margin-top: 0; margin-bottom: 0; color: #7C7D86; font-size: 14px; line-height: 16px; font-family: 'Google Sans', Helvetica, Arial;">To</span>
                                                <a href=""
                                                   style="display: block; margin-top: 4px; margin-bottom: 5px; color: #2f313f !important; font-size: 20px;line-height: 24px; font-family: 'Google Sans', Helvetica, Arial; text-decoration: none !important;cursor: default;"
                                                   class="address-title" x-apple-data-detectors="true">XXX</a>
                                            </div>
                                        </td>
                                    </tr>

                                    <tr>
                                        <td style="padding: 0 16px;">
                                            <div style="background: #F4F4F6;height: 1px;width: 100%;max-width: 600px;margin: 10px auto"></div>
                                        </td>
                                    </tr>

                                    <tr>
                                        <td style="vertical-align: middle; padding: 0 16px;">
                                            <table width="100%" cellpadding="0" cellspacing="0" style="table-layout: fixed;width:100%; border:none; border-collapse:collapse; max-width: 600px; margin-left: auto; margin-right: auto;">
                                                <tr>
                                                    <td style="vertical-align: top; padding: 0;">
                                                        <p style="margin: 0 auto;max-width: 600px; width: 100%;">
                                                        <table style="border: none; border-collapse:collapse;">
                                                            <tr>
                                                                <td style="white-space: nowrap; padding-left: 4px; vertical-align: top;"><span style="display: inline-block; color: #2f313f; font-size: 16px; line-height: 24px; font-family: 'Google Sans', Helvetica, Arial; padding-left: 4px; padding-right: 1px; float: left;">1 &times;</span></td>
                                                                <td><span style="color: #2f313f; font-size: 16px; line-height: 24px; font-family: 'Google Sans', Helvetica, Arial; padding-left: 4px;">Prawns with Spicy 🎁  30% OFF!</span></td>
                                                            </tr>
                                                        </table>
                                                        <span style="display: block; font-size: 14px; line-height: 24px; color: #818391; font-family: 'Google Sans', Helvetica, Arial; padding-left: 39px;">
                                                            Rice Chao Chao
                                                        </span>
                                                        </p>
                                                    </td>
                                                    <td style="vertical-align: top; text-align: right; padding: 0;table-layout: fixed; max-width: 80px; width: 80px;">
                                                        <p style="display: inline-block; color: #2f313f; font-size: 16px; line-height: 24px; font-family: 'Google Sans', Helvetica, Arial; margin-top: 0; margin-bottom: 0;">9.03€</p>
                                                    </td>
                                                </tr>

                                                <tr>
                                                    <td colspan="2" style="padding-bottom: 0; padding-top: 0;">
                                                        <div style="background: #F4F4F6;height: 1px;width: 100%;max-width: 600px;margin: 10px auto"></div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="vertical-align: middle; padding: 0;">
                                                        <p style="margin-top: 6px; margin-bottom: 6px; color: #2f313f; font-size: 16px; line-height: 24px; font-family: 'Google Sans', Helvetica, Arial;">Delivery fee</p>
                                                    </td>
                                                    <td style="vertical-align: middle; text-align: right; padding: 0;">
                                                        <p style="margin-top: 6px; margin-bottom: 6px; color: #2f313f; font-size: 16px; line-height: 24px; font-family: 'Google Sans', Helvetica, Arial;">1.50€</p>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td colspan="2" style="padding: 0;">
                                                        <div style="background: #F4F4F6;height: 1px;width: 100%;max-width: 600px;margin: 10px auto"></div>
                                                    </td>
                                                </tr>

                                                <tr>
                                                    <td style="vertical-align: middle; padding: 0;">
                                                        <p style="margin-top: 6px; margin-bottom: 6px; font-family: 'Google Sans', Helvetica, Arial; color: #2f313f; font-size: 16px; line-height: 24px;">Campaign: NKHLTN1JP8JJTW7</p>
                                                    </td>
                                                    <td style="vertical-align: middle; text-align: right; padding: 0;">
                                                        <p style="margin-top: 6px; margin-bottom: 6px; font-size: 16px;line-height: 24px;font-family: 'Google Sans', Helvetica, Arial;color: #2f313f;white-space: nowrap;">-1.50€</p>
                                                    </td>
                                                </tr>

                                                <tr>
                                                    <td colspan="2" style="padding: 0;">
                                                        <div style="background: #F4F4F6;height: 1px;width: 100%;max-width: 600px;margin: 10px auto"></div>
                                                    </td>
                                                </tr>

                                                <tr>
                                                    <td style="vertical-align: middle; padding: 0;">
                                                        <p style="margin-top: 6px; margin-bottom: 6px; font-family: 'Google Sans', Helvetica, Arial; color: #2f313f; font-size: 20px; line-height: 30px;"><b>Total charged:</b></p>
                                                    </td>
                                                    <td style="vertical-align: middle; text-align: right; padding: 0;">
                                                        <p style="margin-top: 6px;margin-bottom: 6px;font-size: 20px;line-height: 30px;font-family: 'Google Sans', Helvetica, Arial;color: #2f313f;white-space: nowrap;"
                                                        ><b>9.03€</b></p>
                                                    </td>
                                                </tr>

                                                <tr>
                                                    <td style="vertical-align: middle; padding: 0;">
                                                        <p style="margin-top: 6px; margin-bottom: 12px; font-family: 'Google Sans', Helvetica, Arial; color: #2f313f; font-size: 16px; line-height: 24px;">
                                                            <img srcset="https://taxify-static-content-for-public-web.s3.eu-central-1.amazonaws.com/invoicing/email_resource/delivery/visa-2x.png 2x"
                                                                 src="https://taxify-static-content-for-public-web.s3.eu-central-1.amazonaws.com/invoicing/email_resource/delivery/visa-2x.png" width="24" height="24"
                                                                 style="height: 24px; width: 24px; float: left;">
                                                            <span style="padding-left: 10px;">
                                                                    <span>•••• XXXX</span>
                                                            </span>
                                                        </p>
                                                    </td>
                                                    <td style="vertical-align: middle; text-align: right; padding: 0;">
                                                        <p style="margin-top: 0;margin-bottom: 0;font-size: 16px;line-height: 24px;font-family: 'Google Sans', Helvetica, Arial;color: #2f313f;white-space: nowrap;"></p>
                                                    </td>
                                                </tr>

                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <tr>


                            <td class="right-button" style="background: #F4F4F6;padding: 0;">
                                <a href="https:&#x2F;&#x2F;delivery-invoicing.bolt.eu&#x2F;invoice&#x2F;pdf&#x2F;?uuid&#x3D;6c57393c-1e0c-4bb2-865d-bc33e4f46b84&amp;l&#x3D;en&amp;c&#x3D;pt" target="_blank">
                                    <table width="100%" cellpadding="0" cellspacing="0" style="width:100%; border:none; border-collapse:collapse;" class="btn-wrap">
                                        <tr>
                                            <td style="padding: 0;vertical-align: middle;">
                                                <div style="text-decoration: none; color: #7C7D86; font-family: 'Google Sans', Helvetica, Arial; display: inline-block; padding-top: 26px; padding-left: 17px; padding-bottom: 22px;">
                                                    <span style="display: block; font-size: 14px; line-height: 16px; color: #7C7D86;">Download cost document</span>
                                                    <span class="footer-label" style="display: block; font-size: 16px; line-height: 20px; color: #2f313f; padding-top: 4px;">Delivery</span>

                                                </div>
                                            </td>
                                            <td style="padding: 0;vertical-align: middle;">
                                                <img srcset="https://taxify-static-content-for-public-web.s3.eu-central-1.amazonaws.com/invoicing/email_resource/delivery/chevron-2x.png 2x"
                                                     src="https://taxify-static-content-for-public-web.s3.eu-central-1.amazonaws.com/invoicing/email_resource/delivery/chevron-2x.png" width="24" height="24"
                                                     style="height: 24px; width: 24px; margin-top: 8px;">
                                            </td>
                                        </tr>
                                    </table>
                                </a>
                            </td>
                        </tr>

                        <tr>
                            <td colspan="3" style="display: block; font-size: 14px; line-height: 16px; color: #7C7D86; font-family: 'Google Sans', Helvetica, Arial; padding-left: 16px; margin-top: 16px; margin-bottom: 5px;">
                                If you require an invoice for Food, please request it from the Food Provider.
                            </td>
                        </tr>

                        <tr>
                            <td class="under-footer" colspan="3" style="color: #7C7D86; font-size: 12px; height: 18px; line-height: 14px; padding-bottom: 40px; padding-top: 32px; text-align: center; width: 540px;">
                                © 2021 Bolt Operations OÜ
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </div>
</center>
</body>

</html>
"""


@pytest.fixture
def uber_eats_messages() -> Iterable[GmailMessage]:
    return [
        GmailMessage(
            id="17570b788e2319d0",
            sender_email="Sender Email",
            subject="Total €16.95 28 October 2020 Thanks for ordering, Valter Here&#39;s your receipt for Pizza "
            "Lizzy. Total €16.95 2 Pizza Média c/ 4 ingredientes à escolha!!! €14.55 Escolha até 4 "
            "ingredientes Azeite",
            body=None,
            date="Wed, 28 Oct 2020 19:37:56 +0000 (UTC)",
        ),
        GmailMessage(
            id="174a7fef0d8cdef3",
            sender_email="Sender Email",
            subject="Total €10.90 19 September 2020 Thanks for ordering, Valter Here&#39;s your receipt for Poke "
            "House 🐠 (Saldanha). Total €10.90 1 Mixed Seas €8.50 Escolha o tamanho do bowl: Regular €0.00 "
            "Deseja Topping ",
            body=None,
            date="Sat, 19 Sep 2020 20:12:14 +0000 (UTC)",
        ),
    ]


@pytest.fixture
def bolt_food_messages() -> Iterable[GmailMessage]:
    return [
        GmailMessage(
            id="179f7511b28528cd",
            sender_email="Sender Email",
            subject="10-06-2021 Bon Appetit, Valter! This is your receipt. From Chickinho Rua Marquês de Fronteira "
            "117F, 1070-292 Lisboa To XXX, Lisbon 1 Breast Classic Sauce 6.90€ 2 Wedges with Herbs",
            body="""
            ­19-06-2021 
            *Bon Appetit,
            Valter!*
            
            This is your receipt.
            
            From Chickinho ­Rua Marquês de Fronteira 117F, 1070-292 Lisboa
            
            To ­XXX, Lisbon
            
             × 
            
            Delivery fee
            
            1.50€
            
            Small order fee
            
            : 
            
            *Total charged:*
            
            *9.73€*
            
            Download cost document Food
            
            (  )
            
            Download cost document Delivery
            
            If you require an invoice for Food, please request it from the Food Provider. © 2021 Bolt Operations OÜ
            """,
            date="Thu, 10 Jun 2021 19:05:57 +0000 (UTC)",
        ),
        GmailMessage(
            id="17914b9e89b41e02",
            sender_email="Sender Email",
            subject="27-04-2021 Bon Appetit, Valter! This is your receipt. From Sushicome - Saldanha Av. Miguel "
            "Bombarda, 23B - Lisboa 1050161 To XXX, Lisbon 1 BREADED SHRIMP CALIFORNIA (15 pieces) Soy",
            body="""
            ­27-04-2021 
            *Bon Appetit,
            Valter!*
            
            This is your receipt.
            
            From Sushicome - Saldanha ­Av. Miguel Bombarda, 23B - Lisboa 1050161
            
            To ­XXX, Lisbon
            
            Delivery fee
            
            1.50€
            
            Small order fee
            
            : 
            
            *Total charged:*
            
            *15.80€*
            
            Download cost document Food
            
            (  )
            
            Download cost document Delivery
            
            If you require an invoice for Food, please request it from the Food Provider. © 2021 Bolt Operations OÜ
            """,
            date="Tue, 27 Apr 2021 19:06:37 +0000 (UTC)",
        ),
    ]
