"""
expenses/utils.py

Smart category prediction via keyword matching.

predict_category(description) -> str
  Returns a category name (one of the seeded values) or 'Others'.
  The function is written so an ML/NLP model can replace it later:
  just swap out the implementation while keeping the same signature.
"""

# ─── Keyword dictionary ────────────────────────────────────────────────────────
# Each key is a Category name that must match a seeded Category record.
# Values are lists of lowercase keywords to scan for in the description.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    # Check most specific / least ambiguous categories first
    'Entertainment': [
        'netflix', 'spotify', 'hotstar', 'prime video',
        'movie', 'cinema', 'theatre', 'concert', 'game',
        'entertainment', 'gaming',
    ],
    'Groceries': [
        'bigbasket', 'blinkit', 'zepto', 'dmart grocery',
        'vegetables', 'fruits', 'milk', 'supermarket',
        'grocery', 'rice', 'dmart',
    ],
    'Food': [
        'pizza', 'burger', 'restaurant', 'cafe', 'coffee',
        'swiggy', 'zomato', 'lunch', 'dinner', 'breakfast',
        'biryani', 'snacks', 'food', 'eat', 'meal',
    ],
    'Travel': [
        'uber', 'ola', 'taxi', 'bus', 'train', 'flight',
        'petrol', 'fuel', 'metro', 'auto', 'toll', 'travel',
        'cab', 'rapido', 'railway',
    ],
    'Health': [
        'doctor', 'medicine', 'pharmacy', 'hospital', 'gym',
        'clinic', 'health', 'medical', 'fitness', 'yoga',
    ],
    'Education': [
        'udemy', 'coursera', 'book', 'course', 'tuition',
        'exam', 'fees', 'stationery', 'education', 'school',
        'college', 'tutor',
    ],
    'Bills': [
        'electricity', 'water bill', 'wifi', 'internet',
        'recharge', 'rent', 'gas bill', 'mobile bill', 'emi',
        'subscription', 'broadband', 'insurance',
    ],
    'Shopping': [
        'amazon', 'flipkart', 'myntra', 'meesho',
        'clothes', 'shirt', 'shoes', 'mall', 'shop',
    ],
}

# Fallback when no keyword matches
DEFAULT_CATEGORY = 'Others'


def predict_category(description: str) -> str:
    """
    Predict the expense category from the description text.

    Algorithm (O(n·k), fast enough for a single user input):
      1. Lowercase the description.
      2. For each category, check if any keyword appears as a substring.
      3. Return the first matching category, or DEFAULT_CATEGORY.

    Designed so an NLP model (e.g. zero-shot classifier) can replace
    step 2 later without changing the function signature or callers.

    Args:
        description: Raw expense description entered by the user.

    Returns:
        A category name string matching a seeded Category record.
    """
    if not description:
        return DEFAULT_CATEGORY

    lower_desc = description.lower()

    for category_name, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lower_desc:
                return category_name

    return DEFAULT_CATEGORY
