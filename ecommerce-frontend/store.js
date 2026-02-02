/**
 * store.js
 * Handles the main store logic: fetching products, filtering, and reviews.
 */

// State Management
let state = {
    token: localStorage.getItem('accessToken'),
    userLikesMap: {},
    currentSortValue: null,
    currentPageUrl: null,
    debounceTimer: null
};

// Check Auth on Load
if (!state.token) window.location.href = 'login.html';

document.addEventListener('DOMContentLoaded', init);

async function init() {
    await fetchCategories();
    await fetchUserLikes();
    checkUserRole();
    
    // Initial Load
    applyFilters();

    // Event Listeners for Static Elements
    setupEventListeners();
}

function setupEventListeners() {
    // Search Input Debounce
    const searchInput = document.getElementById('searchInput');
    if(searchInput) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(state.debounceTimer);
            state.debounceTimer = setTimeout(() => applyFilters(), 500);
        });
    }

    // Filter Inputs
    document.getElementById('categoryFilter').addEventListener('change', applyFilters);
    document.getElementById('minPrice').addEventListener('change', applyFilters);
    document.getElementById('maxPrice').addEventListener('change', applyFilters);

    // Pagination
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (document.getElementById('prevBtn').dataset.url) {
            fetchProducts(document.getElementById('prevBtn').dataset.url);
        }
    });
    document.getElementById('nextBtn').addEventListener('click', () => {
        if (document.getElementById('nextBtn').dataset.url) {
            fetchProducts(document.getElementById('nextBtn').dataset.url);
        }
    });

    // Event Delegation for Product Grid (Likes, Add to Cart, Reviews)
    document.getElementById('productContainer').addEventListener('click', handleProductGridClick);

    // Review Form
    document.getElementById('reviewForm').addEventListener('submit', handleReviewSubmit);
}

// --- Role Management ---
function checkUserRole() {
    if (state.token) {
        const decoded = parseJwt(state.token);
        if (decoded && decoded.role === 'RETAILER') {
            const retailerBtn = document.getElementById('retailerLink');
            if(retailerBtn) retailerBtn.style.display = 'inline-block';
        }
    }
}

// --- Categories ---
async function fetchCategories() {
    try {
        const res = await authFetch(`${API_BASE}/api/store/categories/`);
        if (res.ok) {
            const data = await res.json();
            const categories = data.results || data;
            
            const navContainer = document.getElementById('navCategoryLinks');
            const selectFilter = document.getElementById('categoryFilter');
            
            // Clear existing to avoid duplicates if re-run
            navContainer.innerHTML = '<a href="#" class="active" data-cat-id="" id="nav-all">All</a>';
            
            // Re-bind "All" link
            document.getElementById('nav-all').addEventListener('click', (e) => handleHeaderFilter(e, ''));

            categories.forEach(cat => {
                // Populate Dropdown
                const opt = document.createElement('option');
                opt.value = cat.id; 
                opt.textContent = cat.name;
                selectFilter.appendChild(opt);

                // Populate Header (Limit to 5)
                if (navContainer.children.length < 6) {
                    const link = document.createElement('a');
                    link.href = "#";
                    link.textContent = cat.name;
                    link.dataset.catId = cat.id; 
                    link.addEventListener('click', (e) => handleHeaderFilter(e, cat.id));
                    navContainer.appendChild(link);
                }
            });
        }
    } catch (e) { console.error("Category Fetch Error:", e); }
}

function handleHeaderFilter(e, catId) {
    e.preventDefault();
    document.getElementById('categoryFilter').value = catId; 
    applyFilters();
}

// --- Sorting ---
// Global scope function because it's called by onclick in HTML (or you can attach listeners)
window.setSort = function(val) {
    state.currentSortValue = val;
    
    // Update UI classes
    document.getElementById('sortNone').className = (val === null) ? 'sort-btn active' : 'sort-btn';
    document.getElementById('sortAsc').className  = (val === 1)    ? 'sort-btn active' : 'sort-btn';
    document.getElementById('sortDesc').className = (val === -1)   ? 'sort-btn active' : 'sort-btn';

    applyFilters();
}

// --- Filtering & Fetching ---
async function applyFilters() {
    const min = document.getElementById('minPrice').value;
    const max = document.getElementById('maxPrice').value;
    const cat = document.getElementById('categoryFilter').value;
    const search = document.getElementById('searchInput').value;

    updateActiveHeaderLink(cat);

    let url = `${API_BASE}/api/store/products/filter_products/?num=9`;
    if (min) url += `&min_price=${min}`;
    if (max) url += `&max_price=${max}`;
    if (cat) url += `&category_id=${cat}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (state.currentSortValue !== null) url += `&sort_by_price=${state.currentSortValue}`;

    await fetchProducts(url);
}

window.clearFilters = function() {
    document.getElementById('minPrice').value = '';
    document.getElementById('maxPrice').value = '';
    document.getElementById('categoryFilter').value = '';
    document.getElementById('searchInput').value = '';
    setSort(null); 
}

function updateActiveHeaderLink(activeCatId) {
    const links = document.querySelectorAll('#navCategoryLinks a');
    links.forEach(link => {
        if (link.dataset.catId == activeCatId || (activeCatId === '' && !link.dataset.catId)) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

async function fetchProducts(url) {
    state.currentPageUrl = url;
    const container = document.getElementById('productContainer');
    container.innerHTML = '<div class="loading-spinner"></div>';
    

    try {
        const response = await authFetch(url);
        console.log(response)
        if (await checkRateLimit(response)) return;
        if (response.status === 401) { logout(); return; }
        
        const data = await response.json();
        
        // Handle Pagination Buttons
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        if (data.previous) {
            prevBtn.disabled = false;
            prevBtn.dataset.url = data.previous;
        } else {
            prevBtn.disabled = true;
            prevBtn.removeAttribute('data-url');
        }

        if (data.next) {
            nextBtn.disabled = false;
            nextBtn.dataset.url = data.next;
        } else {
            nextBtn.disabled = true;
            nextBtn.removeAttribute('data-url');
        }

        updateResultsInfo(data);
        renderProducts(data.results || []);

    } catch (error) {
        console.error("Error:", error);
        container.innerHTML = '<div class="error-state">Failed to load products. Please try again.</div>';
    }
}

function updateResultsInfo(data) {
    const resultsDiv = document.getElementById('resultsInfo');
    const currentCount = data.results ? data.results.length : 0;
    const totalActive = data.total_active_products !== undefined ? data.total_active_products : '-';
    const filteredTotal = data.count !== undefined ? data.count : currentCount;

    // FIX: Remove the 'hidden' class so the element can become visible
    resultsDiv.classList.remove('hidden'); 
    resultsDiv.style.display = 'flex';

    resultsDiv.innerHTML = `
        <span>Showing <strong>${currentCount}</strong> results (Filtered from <strong>${filteredTotal}</strong> matches)</span>
        <span class="total-badge">Total Products: ${totalActive}</span>
    `;
}

function renderProducts(products) {
    const container = document.getElementById('productContainer');
    container.innerHTML = '';

    if (products.length === 0) {
        container.innerHTML = '<div class="empty-state">No products found matching your criteria.</div>';
        return;
    }

    const fragment = document.createDocumentFragment();

    products.forEach(p => {
        const card = document.createElement('div');
        card.className = 'product-card';
        
        console.log(p.image)
    
        
        
        let imgUrl = `${API_BASE}/media/products/dummy.jpg`;

	if (p.image) {
	    if (p.image.startsWith('http')) {
		imgUrl = p.image;
	    } else if (p.image.startsWith('/media/')) {
		imgUrl = `${API_BASE}${p.image}`;
	    } else {
		imgUrl = `${API_BASE}/media/${p.image}`;
	    }
	}
        
        const isLiked = !!state.userLikesMap[p.id];
        const heartClass = isLiked ? 'liked' : '';
        const catTag = p.category ? `<div class="category-tag">${p.category.name}</div>` : '';
        
        // Using data attributes for event delegation
        card.innerHTML = `
            <div class="card-header">
                <span class="stock-badge ${p.amount_in_stock > 0 ? 'in-stock' : 'out-of-stock'}">
                    ${p.amount_in_stock > 0 ? 'In Stock' : 'Out of Stock'} (${p.amount_in_stock})
                </span>
                <button class="like-btn ${heartClass}" data-action="like" data-id="${p.id}">
                    ${isLiked ? '&#9829;' : '&#9825;'}
                </button>
            </div>
            <div class="img-wrapper">
                <img src="${imgUrl}" class="product-img" alt="${p.name}">
            </div>
            <div class="product-info">
                ${catTag}
                <h3>${p.name}</h3>
                <div class="price">$${p.price}</div>
            </div>
            <div class="card-actions">
                <button class="btn-outline" data-action="reviews" data-id="${p.id}" data-name="${p.name}">Reviews</button>
                <button class="btn-primary" data-action="add-to-cart" data-id="${p.id}">Add to Cart</button>
            </div>
        `;
        fragment.appendChild(card);
    });
    container.appendChild(fragment);
}

// --- Event Delegation Logic ---
async function handleProductGridClick(e) {
    const btn = e.target.closest('button');
    if (!btn) return;

    const action = btn.dataset.action;
    const id = btn.dataset.id;

    if (action === 'like') {
        toggleLike(id, btn);
    } else if (action === 'add-to-cart') {
        addToCart(id);
    } else if (action === 'reviews') {
        openReviewModal(id, btn.dataset.name);
    }
}

// --- Actions ---
async function fetchUserLikes() {
    try {
        const res = await authFetch(`${API_BASE}/api/store/liked_product/`);
        if (res.ok) {
            const data = await res.json();
            (data.results || data).forEach(like => {
                const pId = (like.product && like.product.id) ? like.product.id : like.product;
                state.userLikesMap[pId] = true; 
            });
        }
    } catch (e) { console.error(e); }
}

async function toggleLike(productId, btn) {
    const isLiked = state.userLikesMap[productId];
    
    // Optimistic UI Update
    if (isLiked) {
        btn.classList.remove('liked'); 
        btn.innerHTML = '&#9825;'; 
        delete state.userLikesMap[productId];
        // Background sync
        await authFetch(`${API_BASE}/api/store/liked_product/${productId}/`, { method: 'DELETE' });
    } else {
        btn.classList.add('liked'); 
        btn.innerHTML = '&#9829;'; 
        state.userLikesMap[productId] = true;
        await authFetch(`${API_BASE}/api/store/liked_product/`, { method: 'POST', headers: {'Content-Type': 'application/json' }, body: JSON.stringify({ product_id: productId }) });
    }
}

async function addToCart(id) {
    try {
        const res = await authFetch(`${API_BASE}/api/store/cart/`, { method: 'POST', headers: {'Content-Type': 'application/json' }, body: JSON.stringify({ product_id: id, quantity: 1 }) });
        if (await checkRateLimit(res)) return;
        if (res.ok) showToast("Added to cart!","success");
        else { const d = await res.json(); showToast(d.detail || "Failed to add to cart","error"); }
    } catch (e) { console.error(e); }
}

// --- Reviews ---
window.closeReviewModal = function() { document.getElementById('reviewModal').style.display = 'none'; }

async function openReviewModal(pid, pname) {
    resetReviewForm(); 
    document.getElementById('reviewModal').style.display = 'flex';
    document.getElementById('modalTitle').textContent = `Reviews: ${pname}`;
    document.getElementById('reviewProductId').value = pid;
    
    const list = document.getElementById('reviewList');
    list.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const [allReviewsRes, myReviewRes] = await Promise.all([
            //fetch(`${API_BASE}/api/store/reviews/?product_id=${pid}`),
            fetch(`${API_BASE}/api/store/reviews/?product_id=${pid}`, {
    method: "GET",
    headers: {
        "ngrok-skip-browser-warning": "true",
    },
}),
            authFetch(`${API_BASE}/api/store/user_review/${pid}/`).catch(e => null)
        ]);

        const allReviewsData = await allReviewsRes.json();
        let allReviews = allReviewsData.results || allReviewsData;
        
        let myReview = null;
        if (myReviewRes && myReviewRes.ok) {
            myReview = await myReviewRes.json();
        }

        list.innerHTML = '';

        if (myReview) {
            renderMyReview(myReview, pid);
            allReviews = allReviews.filter(r => r.id !== myReview.id);
        }

        if (allReviews.length === 0 && !myReview) {
            list.innerHTML = '<div class="empty-state">No reviews yet. Be the first!</div>';
        } else {
            allReviews.forEach(renderOtherReview);
        }

    } catch (error) {
        console.error(error);
        list.innerHTML = '<div class="error-state">Failed to load reviews.</div>';
    }
}

function renderMyReview(review, pid) {
    const list = document.getElementById('reviewList');
    const d = document.createElement('div');
    d.className = 'review-card my-review'; 
    d.innerHTML = `
        <div class="review-header">
            <div><strong>You</strong> <span class="badge badge-blue">YOUR REVIEW</span></div>
            <div class="star-rating">${'★'.repeat(review.rating)}${'☆'.repeat(5-review.rating)}</div>
        </div>
        <p class="review-body">${review.comment}</p>
        <div class="review-actions">
            <button onclick="editReview(${review.id}, ${review.rating}, '${review.comment.replace(/'/g, "\\'")}')">Edit</button>
            <button class="delete-btn" onclick="deleteReview(${pid})">Delete</button>
        </div>
    `;
    list.appendChild(d);
}

function renderOtherReview(review) {
    const list = document.getElementById('reviewList');
    const d = document.createElement('div');
    d.className = 'review-card';
    const userDisplay = (review.user && review.user.email) ? review.user.email.split('@')[0] : 'User';
    
    d.innerHTML = `
        <div class="review-header">
            <strong>${userDisplay}</strong>
            <div class="star-rating">${'★'.repeat(review.rating)}${'☆'.repeat(5-review.rating)}</div>
        </div>
        <p class="review-body">${review.comment}</p>
    `;
    list.appendChild(d);
}

// Global scope for HTML onclicks inside modal (optional: could be delegated too)
window.editReview = function(id, rating, comment) {
    document.getElementById('reviewFormTitle').textContent = "Edit Your Review";
    document.getElementById('editingReviewId').value = id; 
    document.getElementById('reviewRating').value = rating;
    document.getElementById('reviewComment').value = comment;
    document.getElementById('reviewSubmitBtn').textContent = "Update Review";
    document.getElementById('cancelEditBtn').style.display = 'block';
}

window.resetReviewForm = function() {
    document.getElementById('reviewFormTitle').textContent = "Write a Review";
    document.getElementById('editingReviewId').value = '';
    document.getElementById('reviewRating').value = '';
    document.getElementById('reviewComment').value = '';
    document.getElementById('reviewSubmitBtn').textContent = "Submit Review";
    document.getElementById('cancelEditBtn').style.display = 'none';
}

window.deleteReview = async function(productId) {
    const confirmed = await showConfirm("Are you sure you want to delete this review?");
    if (!confirmed) return;
    
    const res = await authFetch(`${API_BASE}/api/store/user_review/${productId}/`, { method: 'DELETE' });
    if (res.ok) {
        const pname = document.getElementById('modalTitle').textContent.replace('Reviews: ', '');
        openReviewModal(productId, pname);
        showToast("Review deleted", "success");
    } else {
        showToast("Failed to delete review", "error");
    }
}

async function handleReviewSubmit(e) {
    e.preventDefault();
    const pid = document.getElementById('reviewProductId').value;
    const isEditing = document.getElementById('editingReviewId').value;
    const rating = document.getElementById('reviewRating').value;
    const comment = document.getElementById('reviewComment').value;

    let url = `${API_BASE}/api/store/user_review/`;
    let method = 'POST';
    if (isEditing) { url += `${pid}/`; method = 'PATCH'; }

    const res = await authFetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: pid, rating: rating, comment: comment })
    });
    
    if (res.ok) { 
        showToast(isEditing ? "Review Updated!" : "Review Submitted!","success"); 
        resetReviewForm();
        const pname = document.getElementById('modalTitle').textContent.replace('Reviews: ', '');
        openReviewModal(pid, pname);
    } else { 
        const err = await res.json();
        showToast("Error: " + (err.detail || "Could not save review"),"error"); 
    }
}
