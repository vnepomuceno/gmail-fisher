from typing import Iterable

import pytest as pytest

from gmail_fisher.models import GmailMessage


@pytest.fixture
def uber_eats_messages() -> Iterable[GmailMessage]:
    return [
        GmailMessage(
            id="17570b788e2319d0",
            subject="Total €16.95 28 October 2020 Thanks for ordering, Valter Here&#39;s your receipt for Pizza "
            "Lizzy. Total €16.95 2 Pizza Média c/ 4 ingredientes à escolha!!! €14.55 Escolha até 4 "
            "ingredientes Azeite",
            body=None,
            date="Wed, 28 Oct 2020 19:37:56 +0000 (UTC)",
        ),
        GmailMessage(
            id="174a7fef0d8cdef3",
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
