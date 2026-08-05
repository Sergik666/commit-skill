1. Branch: feat/call-for-price-form
2. Commit: add call for price request form to product page
3.1. Redmine title: Call for price request form on product page
3.2.
```textile
h3. Summary

Added a "Call for price" form to the product page controller and template, the form collects name, phone and email, validates them server side and creates a lead in CRM.

h3. Details

The button is shown only for products with the call_for_price flag enabled, and submissions are rate limited per session.
```
4.1. PR title: Add call for price request form
4.2.
```md
## Summary

Added a `Call for price` form to the product page: new controller route, QWeb template, and a CRM lead created on submit.

## Notes

The button appears only for products flagged as call-for-price, and submissions are rate limited per session.
```
