
document.getElementById('recommendation-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const movieInput = document.getElementById('movie-input').value;
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = 'Loading recommendations...';

    try {
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ movie: movieInput }),
        });
        const movies = await response.json();

        if (movies.error) {
            recommendationsDiv.innerHTML = `<p>${movies.error}</p>`;
            return;
        }

        recommendationsDiv.innerHTML = '';
        movies.forEach(movie => {
            const movieCard = document.createElement('div');
            movieCard.className = 'movie-card';
            movieCard.innerHTML = `
                <h3>${movie.title}</h3>
                <img src="${movie.poster_url}" alt="${movie.title} Poster">
                <!-- Add more movie details here if available -->
            `;
            recommendationsDiv.appendChild(movieCard);
        });
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        recommendationsDiv.innerHTML = '<p>Error fetching recommendations. Please try again.</p>';
    }
});
