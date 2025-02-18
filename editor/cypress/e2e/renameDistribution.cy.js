/// <reference types="cypress" />

import "cypress-file-upload";
import "cypress-iframe";

import { VERSIONS } from "../support/constants";

VERSIONS.forEach((version) => {
  const fixture = `${version}/titanic.json`;
  describe(`[Version ${version}] Renaming of FileObjects/FileSets/RecordSets/Fields.`, () => {
    it("should rename the FileObject/FileSet everywhere", () => {
      cy.visit("http://localhost:8501");

      cy.fixture(fixture).then((fileContent) => {
        const file = {
          fileContent,
          fileName: "titanic.json",
          mimeType: "text/json",
        };
        cy.get("[data-testid='stFileUploadDropzone']").attachFile(file, {
          force: true,
          subjectType: "drag-n-drop",
          events: ["dragenter", "drop"],
        });
      });
      cy.enter('[title="components.tabs.tabs_component"]').then((getBody) => {
        getBody().contains("Resources").click();
      });
      cy.enter('[title="components.tree.tree_component"]').then((getBody) => {
        // Click on genders.csv
        getBody().contains("genders.csv").click();
      });
      const input = version == "0.8"? "Name" : "ID"
      cy.get(`input[aria-label="${input}:red[*]"][value="genders.csv"]`).type(
        "{selectall}{backspace}the-new-name{enter}"
      );

      cy.enter('[title="components.tabs.tabs_component"]').then((getBody) => {
        getBody().contains("Record Sets").click();
      });
      cy.contains("genders").click();
      cy.contains("Edit fields details").click({ force: true });
      cy.contains("the-new-name");
    });
  });
});
