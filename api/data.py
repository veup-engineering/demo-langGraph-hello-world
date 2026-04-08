"""Pre-canned data served by the API.

Lives in-memory so the demo has zero setup. In a real app these would be
database models — the API contract stays the same either way.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Article:
    id: int
    title: str
    category: str
    body: str


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    category: str
    price: float
    description: str


KNOWLEDGE_BASE: list[Article] = [
    Article(
        id=1,
        title="How to reset your password",
        category="account",
        body=(
            "To reset your password, click 'Forgot password' on the login page "
            "and enter the email address on your account. You will receive a "
            "reset link valid for 30 minutes. If the email does not arrive "
            "within five minutes, check your spam folder or contact support."
        ),
    ),
    Article(
        id=2,
        title="Refund policy",
        category="billing",
        body=(
            "We offer a full refund on any purchase within 30 days of the "
            "order date. Refunds are issued to the original payment method "
            "and typically appear within 5-10 business days. Digital goods "
            "that have been downloaded are non-refundable."
        ),
    ),
    Article(
        id=3,
        title="Shipping times and tracking",
        category="shipping",
        body=(
            "Standard shipping takes 3-5 business days within the continental "
            "US. Express shipping is 1-2 business days. International orders "
            "ship in 7-14 business days. A tracking number is emailed when "
            "the order leaves our warehouse."
        ),
    ),
    Article(
        id=4,
        title="Contacting support",
        category="account",
        body=(
            "Support is available 9am-6pm Pacific time, Monday through "
            "Friday, at support@example.com. Average first-response time is "
            "under four hours during business hours."
        ),
    ),
    Article(
        id=5,
        title="Account security best practices",
        category="account",
        body=(
            "Enable two-factor authentication from your account settings. "
            "Use a unique password managed by a password manager. Never "
            "share your verification codes with anyone — support staff will "
            "never ask for them."
        ),
    ),
    Article(
        id=6,
        title="Subscription plans",
        category="billing",
        body=(
            "We offer Free, Pro ($12/month), and Team ($30/user/month) plans. "
            "Pro unlocks unlimited projects and priority support. Team adds "
            "shared workspaces and SSO. You can upgrade or downgrade at any "
            "time from the billing page."
        ),
    ),
]


PRODUCTS: list[Product] = [
    Product(
        id=1,
        name="Acme Widget",
        category="hardware",
        price=19.99,
        description=(
            "A reliable, all-purpose widget. Great for prototyping and small "
            "projects. Comes with a one-year warranty."
        ),
    ),
    Product(
        id=2,
        name="Acme Widget Pro",
        category="hardware",
        price=49.99,
        description=(
            "The professional-grade widget. Stronger materials, longer "
            "lifespan, and a two-year warranty. Recommended for production "
            "deployments."
        ),
    ),
    Product(
        id=3,
        name="Gizmo Starter Kit",
        category="kits",
        price=89.00,
        description=(
            "Everything you need to build your first gizmo: chassis, three "
            "widgets, a sprocket assembly, and step-by-step instructions."
        ),
    ),
    Product(
        id=4,
        name="Sprocket Assembly",
        category="parts",
        price=12.50,
        description=(
            "Replacement sprocket assembly compatible with all Acme widget "
            "and gizmo lines. Sold individually."
        ),
    ),
    Product(
        id=5,
        name="Doohickey 3000",
        category="hardware",
        price=129.00,
        description=(
            "Our flagship doohickey. Wireless, rechargeable, and supports "
            "the open Doohickey Protocol. Two-year warranty included."
        ),
    ),
]


def search_articles(query: str) -> list[Article]:
    """Naive case-insensitive substring + token match over title/body."""
    q = (query or "").strip().lower()
    if not q:
        return list(KNOWLEDGE_BASE)
    tokens = [t for t in q.split() if t]
    scored: list[tuple[int, Article]] = []
    for art in KNOWLEDGE_BASE:
        haystack = f"{art.title}\n{art.category}\n{art.body}".lower()
        score = sum(haystack.count(t) for t in tokens)
        if score:
            scored.append((score, art))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [a for _, a in scored]


def search_products(query: str) -> list[Product]:
    q = (query or "").strip().lower()
    if not q:
        return list(PRODUCTS)
    tokens = [t for t in q.split() if t]
    scored: list[tuple[int, Product]] = []
    for p in PRODUCTS:
        haystack = f"{p.name}\n{p.category}\n{p.description}".lower()
        score = sum(haystack.count(t) for t in tokens)
        if score:
            scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]
