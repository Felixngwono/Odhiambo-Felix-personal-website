 // JavaScript for Pagination
 let currentPage = 1;
 const sections = document.querySelectorAll('.section');
 const sectionsPerPage = 2; // Number of sections to show per page
 
 // Function to show sections for the current page
 function showPage(page) {
   let start = (page - 1) * sectionsPerPage;
   let end = start + sectionsPerPage;
 
   sections.forEach((section, index) => {
     section.style.display = (index >= start && index < end) ? 'block' : 'none';
   });
 
   // Disable "Previous" button if on the first page
   document.getElementById('prevBtn').disabled = (page === 1);
   // Disable "Next" button if on the last page
   document.getElementById('nextBtn').disabled = (page === Math.ceil(sections.length / sectionsPerPage));
 }
 
 // Show the first page by default
 showPage(currentPage);
 
 // Add event listeners for pagination buttons
 document.getElementById('prevBtn').addEventListener('click', () => {
   if (currentPage > 1) {
     currentPage--;
     showPage(currentPage);
   }
 });
 
 document.getElementById('nextBtn').addEventListener('click', () => {
   if (currentPage < Math.ceil(sections.length / sectionsPerPage)) {
     currentPage++;
     showPage(currentPage);
   }
 });