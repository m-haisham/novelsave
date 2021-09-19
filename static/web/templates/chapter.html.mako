<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>${novel.title} | ${chapter_wrapper['chapter'].title}</title>
        <link rel="stylesheet" href="../assets/css/bootstrap.min.css">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-light bg-light shadow-sm mb-3">
            <div class="container">
                <span class="navbar-brand">
                    <a class="navbar-brand me-1" href="../index.html">${novel.title}</a>
                </span>
            </div>
        </nav>

        <div class="container">
            <!-- Content -->
            <article>
                <h2 class="mb-4">${chapter_wrapper['chapter'].title}</h2>
                ${content}
            </article>

            <!-- Navigation -->
            <div class="d-flex flex-column flex-md-row justify-content-between gap-2 mb-3">
                % if chapter_wrapper['previous']:
                <a href="../${chapter_wrapper['previous']['filename']}" class="btn btn-light">
                    <span class="badge bg-secondary">PREVIOUS</span>
                    ${chapter_wrapper['previous']['chapter'].title}
                </a>
                % else:
                <div></div>
                % endif

                % if chapter_wrapper['next']:
                <a href="${chapter_wrapper['next']['filename']}" class="btn btn-light">
                    ${chapter_wrapper['next']['chapter'].title}
                    <div>
                        <span class="badge bg-secondary">NEXT</span>
                    </div>
                </a>
                % else:
                <div></div>
                % endif
            </div>
        </div>
    </body>
</html>
