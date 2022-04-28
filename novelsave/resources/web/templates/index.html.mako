<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>${static['bootstrap.min.css']}</style>
        <style>${static['main.css']}</style>
        <title>${novel.title}</title>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4 shadow-sm">
            <div class="container">
                <a class="navbar-brand me-1 text-wrap" href="">${novel.title}</a>
            </div>
        </nav>

        <main class="container">
            <section class="mb-4">
                <div class="card mb-4">
                    <div class="list-group list-group-flush">
                        <div class="list-group-item">
                            <div class="row flex-column flex-md-row">
                                <div class="col-12 col-md-3 fw-bold">Author:</div>
                                <div class="col ms-2 ms-md-0">${novel.author}</div>
                            </div>
                        </div>
                        % for label, values in metadata.items():
                            <div class="list-group-item">
                                <div class="row flex-column flex-md-row">
                                    <div class="col-12 col-md-3 fw-bold">${label.capitalize()}</div>
                                    <div class="col ms-2 ms-md-0">${', '.join(values)}</div>
                                </div>
                            </div>
                        % endfor
                        <div class="list-group-item">
                            <div class="row flex-column flex-md-row">
                                <div class="col-12 col-md-3 fw-bold">Sources:</div>
                                <div class="col ms-2 ms-md-0">
                                    ${', '.join(sources)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header fw-bold">Synopsis</div>
                    <div class="card-body">
                        % for line in novel.synopsis.splitlines():
                            <p>${line}</p>
                        % endfor
                    </div>
                </div>
            </section>

            <section class="mb-4">
            % for volume_wrapper in volume_wrappers:
                % for chapter_wrapper in volume_wrapper['chapter_wrappers']:
                <hr />
                <article id="${chapter_wrapper['id']}" class="mb-4">
                    <h2 class="mb-4">${chapter_wrapper['chapter'].title}</h2>
                    <div class="chapter-content">
                        ${chapter_wrapper['content']}
                    </div>
                </article>
                % endfor
            % endfor
            </section>
        </main>
        <script>${static['bootstrap.min.js']}</script>
    </body>
</html>
