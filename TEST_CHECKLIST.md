# Test Checklist for Dynamic Pricing

## Manual Testing Checklist

### 1. Venue Submission Form
- [ ] Navigate to venue submission page
- [ ] Verify "Pricing Type" radio buttons appear (HOURLY / FLAT)
- [ ] Select "Hourly Rate" - verify hourly price input shows, flat price hides
- [ ] Enter hourly price (e.g., 2000)
- [ ] Select "Flat Rate" - verify flat price input shows, hourly price hides
- [ ] Enter flat price (e.g., 5000)
- [ ] Try submitting with HOURLY selected but no hourly price - verify validation error
- [ ] Try submitting with FLAT selected but no flat price - verify validation error
- [ ] Submit valid form - verify venue is created

### 2. Service Submission Form
- [ ] Navigate to service submission page
- [ ] Verify "Pricing Type" radio buttons appear
- [ ] Test same toggling behavior as venue form
- [ ] Verify validation works
- [ ] Submit valid form - verify service is created

### 3. Venue Detail Page
- [ ] View a HOURLY venue - verify price shows as "৳X / hour"
- [ ] View a FLAT venue - verify price shows as "৳X flat"
- [ ] Check related venues section - verify prices display correctly

### 4. Service Detail Page
- [ ] View a HOURLY service - verify price displays correctly
- [ ] View a FLAT service - verify price displays correctly
- [ ] Check related services section - verify consistent display

### 5. Admin Interface - Venues
- [ ] Login to Django admin
- [ ] Go to Venues list
- [ ] Verify "Price" column shows formatted prices (e.g., "৳2000 / hour")
- [ ] Click on a venue to edit
- [ ] Verify pricing fields are organized in "Capacity & Pricing" section
- [ ] Try saving HOURLY venue without hourly_price - verify validation
- [ ] Try saving FLAT venue without flat_price - verify validation
- [ ] Filter by "Pricing type" - verify filter works

### 6. Admin Interface - Services
- [ ] Go to Services list
- [ ] Verify "Price" column shows formatted prices
- [ ] Edit a service - verify pricing fields layout
- [ ] Test validation same as venues
- [ ] Filter by pricing type

### 7. Booking Creation - HOURLY Venue
- [ ] Create booking for HOURLY venue
- [ ] Set event time: 2pm to 5pm (3 hours)
- [ ] If venue is ৳2000/hour, verify venue_cost = ৳6000
- [ ] Complete booking - check total cost includes venue cost

### 8. Booking Creation - FLAT Venue
- [ ] Create booking for FLAT venue
- [ ] Set event time: 2pm to 10pm (8 hours)
- [ ] If venue is ৳5000 flat, verify venue_cost = ৳5000 (not ৳40000)
- [ ] Complete booking - check total cost

### 9. Service Booking - HOURLY Service
- [ ] Add HOURLY service to booking
- [ ] Set quantity = 4
- [ ] If service is ৳500/hour, verify service_cost = ৳2000
- [ ] Check booking total includes service cost

### 10. Service Booking - FLAT Service
- [ ] Add FLAT service to booking
- [ ] Set quantity = 10
- [ ] If service is ৳1200 flat, verify service_cost = ৳1200 (not ৳12000)
- [ ] Check booking total

### 11. Data Integrity
- [ ] Run: `python test_pricing.py`
- [ ] Verify all tests pass
- [ ] Check for any missing price data warnings

### 12. Edge Cases
- [ ] Try creating venue with both hourly and flat prices set - verify form only saves the selected type's price
- [ ] Edit existing venue from HOURLY to FLAT - verify price switches correctly
- [ ] Edit existing service from FLAT to HOURLY - verify price switches correctly
- [ ] Create booking with venue costing ৳0 - verify it works
- [ ] Check decimal precision (e.g., ৳2500.50) - verify displays and calculates correctly

## Automated Test Cases

### Test 1: Hourly Venue Cost Calculation
```python
# Given: Hourly venue at ৳100/hr
# When: Booking for 3 hours
# Then: Cost should be ৳300
```
**Status**: ✅ PASSED (see test_pricing.py)

### Test 2: Flat Venue Cost Calculation
```python
# Given: Flat venue at ৳500
# When: Booking for 3 hours
# Then: Cost should be ৳500 (duration ignored)
```
**Status**: ⚠️ No flat venues to test yet

### Test 3: Hourly Service Cost Calculation
```python
# Given: Hourly service at ৳50/hr
# When: Quantity = 4
# Then: Cost should be ৳200
```
**Status**: ⚠️ No hourly services to test yet

### Test 4: Flat Service Cost Calculation
```python
# Given: Flat service at ৳200
# When: Quantity = 5
# Then: Cost should be ৳200 (quantity ignored)
```
**Status**: ✅ PASSED (see test_pricing.py)

## Sample Test Data

### Create Test Hourly Venue
```python
venue = Venue.objects.create(
    name="Test Hourly Venue",
    description="Test description",
    location="Test Location",
    city="Dhaka",
    address="123 Test St",
    capacity=100,
    pricing_type='HOURLY',
    hourly_price=2000,
    flat_price=None,
    owner=user,
    status='approved'
)
```

### Create Test Flat Venue
```python
venue = Venue.objects.create(
    name="Test Flat Venue",
    description="Test description",
    location="Test Location",
    city="Dhaka",
    address="123 Test St",
    capacity=100,
    pricing_type='FLAT',
    hourly_price=None,
    flat_price=5000,
    owner=user,
    status='approved'
)
```

### Create Test Hourly Service
```python
service = Service.objects.create(
    name="Test Hourly Service",
    description="Test description",
    category=category,
    pricing_type='HOURLY',
    hourly_price=500,
    flat_price=None,
    provider=user,
    status='approved'
)
```

### Create Test Flat Service
```python
service = Service.objects.create(
    name="Test Flat Service",
    description="Test description",
    category=category,
    pricing_type='FLAT',
    hourly_price=None,
    flat_price=1200,
    provider=user,
    status='approved'
)
```

## Known Issues / Future Enhancements

### Current Limitations
1. Admin interface doesn't dynamically hide/show price fields based on pricing_type selection (requires custom JavaScript)
2. Venue/service list filters still use old price range logic
3. No visual indicator in list views showing which pricing type is used

### Future Enhancements
1. Add admin JavaScript for dynamic field hiding (using Media class already added)
2. Update list/search views to handle both pricing types in filters
3. Add pricing type icon in list views
4. Add bulk admin action to convert pricing types
5. Add analytics/reports for pricing type distribution

## Rollback Plan

If issues are found:

```bash
# Rollback venues migration
python manage.py migrate venues 0008

# Rollback services migration
python manage.py migrate services 0006

# This will restore old fields (price_per_hour, base_price, price_type)
# Data loss: Any new FLAT pricing entries will be lost
```

## Migration Safety

✅ **Safe to run in production**: 
- Migrations include data migration logic
- Reversible operations
- No data loss for existing records
- New fields are nullable during transition

⚠️ **Caution**:
- Backup database before running migrations in production
- Test on staging environment first
- Monitor for any validation errors after deployment
- Be prepared to rollback if issues arise

## Success Criteria

✅ All manual test cases pass
✅ Automated tests pass
✅ No data integrity issues
✅ Admin interface usable
✅ Booking calculations correct
✅ No breaking changes to existing functionality
✅ Performance impact negligible
