// ── All trip/group data ────────────────────────────────────
const trips = [
  {
    id: 1, dest: 'PARIS', city: 'paris', country: 'France',
    image: 'images/paris.jpg', handle: '@sleepy_head17', initials: 'SH',
    bio: 'Looking for jobless ppl :)', dates: '14.05.2027 – 10.06.2027', duration: '28 nights',
    spotsFilled: 3, spotsTotal: 5, terrain: ['cultural'], style: ['cultural'],
    itinerary: [
      { day: 'Day 1: Arrival & Evening Stroll', activities: ['Land at Charles de Gaulle Airport.', 'Check into our hotel in the Marais district.', 'Evening walk along the Seine and stop at Notre Dame.'] },
      { day: 'Day 2: Iconic Landmarks', activities: ['Morning visit to the Eiffel Tower.', 'Picnic lunch at Champ de Mars.', 'Louvre Museum guided tour in the afternoon.'] },
      { day: 'Day 3: Art & Culture', activities: ['Explore Montmartre and the Sacré-Cœur Basilica.', 'Visit local art studios and markets.'] },
      { day: 'Day 4: Day Trip to Versailles', activities: ['Guided palace tour and gardens exploration.', 'Return to Paris for a Seine River dinner cruise.'] },
      { day: 'Day 5: Last-Minute Shopping & Departure', activities: ['Visit Galeries Lafayette and local boutiques.', 'Farewell coffee before heading to the airport.'] },
    ],
    costBreakdown: [
      { label: 'Accommodation', value: '₹3,500/night (shared double room)' },
      { label: 'Flights (approx.)', value: '₹55,000' },
      { label: 'Local Transportation', value: '₹4,500 (metro pass + transfers)' },
      { label: 'Activities & Tours', value: '₹8,500' },
      { label: 'Total Estimated Cost', value: '₹1,14,000 per person', isTotal: true },
    ],
  },
  {
    id: 2, dest: 'PARIS', city: 'paris', country: 'France',
    image: 'images/paris.jpg', handle: '@jet_lag_jen', initials: 'JL',
    bio: 'Foodies & museum lovers 🥐', dates: '02.06.2027 – 15.06.2027', duration: '13 nights',
    spotsFilled: 5, spotsTotal: 5, terrain: ['cultural'], style: ['cultural', 'food'],
    itinerary: [
      { day: 'Day 1: Arrive & Settle In', activities: ['Arrive at CDG, transfer to hotel.', 'Dinner at a classic Parisian brasserie.'] },
      { day: 'Day 2-3: Food & Museums', activities: ['Guided food tour of Le Marais.', "Visit the Musée d'Orsay.", 'Cooking class — French pastries.'] },
    ],
    costBreakdown: [
      { label: 'Accommodation', value: '₹3,200/night (shared)' },
      { label: 'Flights (approx.)', value: '₹52,000' },
      { label: 'Food & Tours', value: '₹12,000' },
      { label: 'Total Estimated Cost', value: '₹98,000 per person', isTotal: true },
    ],
  },
  {
    id: 3, dest: 'MIAMI', city: 'miami', country: 'USA',
    image: 'images/miami.jpg', handle: '@beach_hopper', initials: 'BH',
    bio: 'Sun, sand & salsa 🌴', dates: '01.08.2027 – 10.08.2027', duration: '9 nights',
    spotsFilled: 2, spotsTotal: 4, terrain: ['beach'], style: ['adventurous'],
    itinerary: [
      { day: 'Day 1: Arrive & Hit the Beach', activities: ['Check into South Beach hotel.', 'Sunset walk on Ocean Drive.'] },
      { day: 'Day 2-3: Art Deco & Nightlife', activities: ['Art Deco Historic District walking tour.', 'Wynwood Walls street art.', 'Night out on Collins Avenue.'] },
      { day: 'Day 4-5: Water Adventures', activities: ['Kayaking in Biscayne Bay.', 'Day trip to Everglades National Park.'] },
    ],
    costBreakdown: [
      { label: 'Accommodation', value: '₹4,200/night (shared)' },
      { label: 'Flights (approx.)', value: '₹42,000' },
      { label: 'Activities & Transport', value: '₹10,000' },
      { label: 'Total Estimated Cost', value: '₹88,000 per person', isTotal: true },
    ],
  },
  {
    id: 4, dest: 'TOKYO', city: 'tokyo', country: 'Japan',
    image: 'images/tokyo.jpg', handle: '@neon_nomad', initials: 'NN',
    bio: 'Anime, ramen & neon lights 🍜', dates: '10.07.2027 – 25.07.2027', duration: '15 nights',
    spotsFilled: 2, spotsTotal: 4, terrain: ['cultural'], style: ['cultural', 'adventurous'],
    itinerary: [
      { day: 'Day 1: Arrive in Tokyo', activities: ['Land at Narita, take Narita Express to city.', 'Check in, explore Shinjuku at night.'] },
      { day: 'Day 2-3: Classic Tokyo', activities: ['Senso-ji Temple in Asakusa.', 'Akihabara electronics & anime district.', 'Ramen tour in Shibuya.'] },
      { day: 'Day 4-5: Day Trips', activities: ['Day trip to Nikko National Park.', 'Hakone — Mt Fuji views & onsen.'] },
    ],
    costBreakdown: [
      { label: 'Accommodation', value: '₹3,800/night (shared)' },
      { label: 'Flights (approx.)', value: '₹48,000' },
      { label: 'JR Pass (transport)', value: '₹18,000' },
      { label: 'Food & Activities', value: '₹11,000' },
      { label: 'Total Estimated Cost', value: '₹1,05,000 per person', isTotal: true },
    ],
  },
  {
    id: 5, dest: 'BALI', city: 'bali', country: 'Indonesia',
    image: 'images/bali.jpg', handle: '@zen_wanderer', initials: 'ZW',
    bio: 'Yoga, rice fields & sunsets 🌅', dates: '15.09.2027 – 30.09.2027', duration: '15 nights',
    spotsFilled: 3, spotsTotal: 6, terrain: ['beach', 'forests'], style: ['adventurous', 'spiritual'],
    itinerary: [
      { day: 'Day 1: Arrive in Bali', activities: ['Land at Ngurah Rai International Airport.', 'Transfer to Ubud, check in to villa.'] },
      { day: 'Day 2-3: Ubud Culture', activities: ['Tegallalang Rice Terraces at sunrise.', 'Ubud Monkey Forest.', 'Traditional Balinese cooking class.'] },
      { day: 'Day 4-5: Temples & Beaches', activities: ['Tanah Lot Temple at sunset.', 'Seminyak beach day.', 'Uluwatu Temple cliff walk.'] },
    ],
    costBreakdown: [
      { label: 'Accommodation', value: '₹2,800/night (villa shared)' },
      { label: 'Flights (approx.)', value: '₹32,000' },
      { label: 'Transport & Activities', value: '₹9,000' },
      { label: 'Food', value: '₹7,000' },
      { label: 'Total Estimated Cost', value: '₹72,000 per person', isTotal: true },
    ],
  },
  {
    id: 6, dest: 'TOKYO', city: 'tokyo', country: 'Japan',
    image: 'images/tokyo.jpg', handle: '@sakura_chaser', initials: 'SC',
    bio: 'Cherry blossoms & street food 🌸', dates: '25.03.2027 – 05.04.2027', duration: '11 nights',
    spotsFilled: 1, spotsTotal: 3, terrain: ['cultural'], style: ['cultural', 'food'],
    itinerary: [
      { day: 'Day 1-2: Arrive & Hanami', activities: ['Arrive, settle in Harajuku area.', 'Yoyogi Park cherry blossom picnic.'] },
      { day: 'Day 3-4: Neighbourhoods', activities: ['Harajuku fashion streets.', 'Shimokitazawa vintage market.', 'Tsukiji outer market breakfast.'] },
    ],
    costBreakdown: [
      { label: 'Accommodation', value: '₹3,600/night (shared)' },
      { label: 'Flights (approx.)', value: '₹46,000' },
      { label: 'Activities & Food', value: '₹13,000' },
      { label: 'Total Estimated Cost', value: '₹95,000 per person', isTotal: true },
    ],
  },
  {
    id: 7, dest: 'HIMALAYAS', city: 'himalayas', country: 'Nepal',
    image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&q=80',
    handle: '@peak_seeker', initials: 'PS',
    bio: 'Everest Base Camp — serious trekkers only 🏔️', dates: '01.09.2027 – 20.09.2027', duration: '19 nights',
    spotsFilled: 4, spotsTotal: 6, terrain: ['mountains'], style: ['trekking', 'adventurous'],
    itinerary: [
      { day: 'Day 1-2: Kathmandu', activities: ['Visa & gear check.', 'Pashupatinath temple visit.'] },
      { day: 'Day 3-12: EBC Trek', activities: ['Namche Bazaar acclimatisation.', 'Tengboche monastery.', 'Everest Base Camp.'] },
      { day: 'Day 13-19: Descent', activities: ['Kala Patthar sunrise view.', 'Return to Lukla.', 'Kathmandu markets.'] },
    ],
    costBreakdown: [
      { label: 'Flights to Kathmandu', value: '₹58,000' },
      { label: 'Trek Permit', value: '₹6,700' },
      { label: 'Guide & Porter', value: '₹16,500' },
      { label: 'Accommodation & Food', value: '₹25,000' },
      { label: 'Total Estimated Cost', value: '₹1,06,200 per person', isTotal: true },
    ],
  },
  {
    id: 8, dest: 'MALDIVES', city: 'maldives', country: 'Indian Ocean',
    image: 'https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=600&q=80',
    handle: '@island_drift', initials: 'ID',
    bio: 'Overwater bungalows & snorkelling 🐠', dates: '20.12.2027 – 30.12.2027', duration: '10 nights',
    spotsFilled: 2, spotsTotal: 4, terrain: ['beach', 'islands'], style: ['luxury'],
    itinerary: [
      { day: 'Day 1-2: Arrival', activities: ['Seaplane transfer to resort.', 'Sunset snorkelling.'] },
      { day: 'Day 3-8: Island Life', activities: ['Dolphin watching cruise.', 'Coral reef diving.', 'Private beach dining.'] },
    ],
    costBreakdown: [
      { label: 'Flights', value: '₹65,000' },
      { label: 'Resort (overwater villa)', value: '₹1,20,000' },
      { label: 'Activities', value: '₹18,000' },
      { label: 'Total Estimated Cost', value: '₹2,03,000 per person', isTotal: true },
    ],
  },
];

const destinations = [
  { id: 'france',    name: 'France',    city: 'paris',     image: 'images/paris.jpg', tags: ['cultural'], desc: "From the sun-kissed vineyards to the shimmering lights of Paris, discover the journey you've always dreamed of..." },
  { id: 'miami',     name: 'Miami',     city: 'miami',     image: 'images/miami.jpg', tags: ['beach', 'adventurous'], desc: 'Feel the rhythm of the ocean, the warmth of the sun, come find your vibe in Miami...' },
  { id: 'tokyo',     name: 'Tokyo',     city: 'tokyo',     image: 'images/tokyo.jpg', tags: ['cultural', 'adventurous'], desc: 'Neon lights meet ancient temples — Tokyo is a city unlike any other...' },
  { id: 'bali',      name: 'Bali',      city: 'bali',      image: 'images/bali.jpg',  tags: ['beach', 'forests', 'spiritual'], desc: "Rice terraces, sacred temples and crystal waters — Bali is the soul of every wanderer's dream..." },
  { id: 'himalayas', name: 'Himalayas', city: 'himalayas', image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&q=80', tags: ['mountains', 'trekking'], desc: 'Epic treks through the roof of the world — the ultimate adventure awaits...' },
  { id: 'maldives',  name: 'Maldives',  city: 'maldives',  image: 'https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=600&q=80', tags: ['beach', 'luxury'], desc: 'Crystal clear waters and overwater bungalows — paradise found...' },
];

// ── Render a trip card HTML ─────────────────────────────────
function renderTripCard(trip) {
  const isFull = trip.spotsFilled >= trip.spotsTotal;
  const bubbleCount = Math.min(trip.spotsFilled, 4);
  const bubbles = Array.from({ length: bubbleCount })
    .map((_, i) => `<div class="spot-bubble">${String.fromCharCode(65 + i)}</div>`).join('');
  return `
    <div class="trip-card" onclick="openDetail(${trip.id})">
      <div class="trip-img-wrap">
        <img src="${trip.image}" alt="${trip.dest}" loading="lazy"/>
        <div class="trip-img-overlay"><span class="trip-dest-name">${trip.dest}</span></div>
      </div>
      <div class="trip-card-body">
        <div class="trip-user-row">
          <div class="trip-avatar">${trip.initials}</div>
          <div><p class="trip-handle">${trip.handle}</p><p class="trip-bio">${trip.bio}</p></div>
        </div>
        <div class="trip-card-footer">
          <div class="trip-spots-row">
            <div class="spots-stack">${bubbles}</div>
            <span class="spots-text">${trip.spotsFilled}/${trip.spotsTotal} spots</span>
          </div>
          <button class="btn-join ${isFull ? 'full' : ''}" onclick="event.stopPropagation();${isFull ? '' : `openDetail(${trip.id})`}">
            ${isFull ? '<i class="fa-solid fa-lock"></i> Full' : '<i class="fa-solid fa-plus"></i> Join'}
          </button>
        </div>
      </div>
    </div>`;
}

function openDetail(tripId) {
  sessionStorage.setItem('mtm_trip', tripId);
  window.location.href = 'detail.html';
}

function getRecommendedTrips(limit = 5) {
  const user = JSON.parse(sessionStorage.getItem('mtm_user') || '{}');
  const prefs = [...(user.terrain || []), ...(user.style || [])].map(s => s.toLowerCase());
  if (!prefs.length) return trips.slice(0, limit);
  const scored = trips.map(t => ({
    ...t,
    score: [...(t.terrain || []), ...(t.style || [])].filter(tag => prefs.includes(tag)).length
  }));
  return scored.sort((a, b) => b.score - a.score).slice(0, limit);
}
