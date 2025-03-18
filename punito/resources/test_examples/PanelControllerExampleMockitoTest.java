/*
 * Copyright (c) 2024 ITZBund. All rights reserved.
 */
package de.itzbund.moeve.enst.taxation.taxation.dlg.af202.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.Test;
import org.mapstruct.factory.Mappers;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Spy;

import de.itzbund.moeve.basis.arch.common.componentstructure.test.MoeveUnitMockitoTest;
import de.itzbund.moeve.basis.arch.common.exception.MoeveBusinessException;
import de.itzbund.moeve.basis.arch.test.TestDataHelper;
import de.itzbund.moeve.enst.taxation.taxation.dlg.af200.model.TaxDeclarationModelBean;
import de.itzbund.moeve.enst.taxation.taxation.dlg.af202.model.mapper.ProcessTaxDeclarationMapper;
import de.itzbund.moeve.enst.taxation.taxation.srv.api.local.Ds141TaxDeclarationServiceLocalFacade;
import de.itzbund.moeve.vvst.common.datatypes.CaseTypeDt;
import de.itzbund.moeve.vvst.common.datatypes.ScreenOperationModeDt;
import de.itzbund.moeve.vvst.common.dlg.model.TabViewParamModelBean;
import de.itzbund.moeve.vvst.common.dlg.test.AbstractVvstControllerMockitoTest;
import de.itzbund.moeve.vvst.taxation.taxation.srv.api.local.LocalTaxationFacade;
import de.itzbund.moeve.vvst.taxation.taxationgeneral.dlg.af202.model.Af202CompletionOfProcessingGeneralPanelModelBean;
import de.itzbund.moeve.vvst.taxation.taxationgeneral.dlg.common.model.OverviewTaxAssessmentModelBean;
import de.itzbund.moeve.vvst.taxation.taxationgeneral.dlg.common.model.TaxDeclarationOverviewModelBean;

@MoeveUnitMockitoTest
public class PanelControllerExampleMockitoTest extends AbstractVvstControllerMockitoTest
{

    private static final boolean                                 RISK_ENABLED                = true;

    private static final boolean                                 RISK_DISABLED               = false;

    private static final String                                  UNIQUE_RISK                 = "UniqueRisk";

    private static final String                                  RISK2                       = "risk2";

    private static final String                                  RISK1                       = "risk1";

    @InjectMocks
    private Af202EnergyCompletionOfProcessingPanelControllerBean sut;

    @Mock
    private ProcessTaxDeclarationMapper                          processTaxDeclarationMapper = Mappers
            .getMapper(ProcessTaxDeclarationMapper.class);

    @Mock
    private Ds141TaxDeclarationServiceLocalFacade                ds141TaxDeclarationServiceLocalFacade;

    @Mock
    private LocalTaxationFacade                                  taxationFacade;

    @Mock
    private TabViewParamModelBean                                tabViewParamModelBean;

    /*
     * TestCase for
     * when SelectionTaxReliefForShippingOrAviation is null;
     */
    @Test
    public void shouldHandlePanelOpenWhenSelectionTaxReliefForShippingOrAviationIsNull() throws MoeveBusinessException
    {
        // given
        Af202CompletionOfProcessingGeneralPanelModelBean completionOfProcessingGeneralPanelModelBean =
                new Af202CompletionOfProcessingGeneralPanelModelBean();

        OverviewTaxAssessmentModelBean overviewTaxAssessmentModelBean = new OverviewTaxAssessmentModelBean();
        overviewTaxAssessmentModelBean.setSelectionTaxReliefForShippingOrAviation(null);

        completionOfProcessingGeneralPanelModelBean.setOverviewTaxAssessmentModelBean(
                overviewTaxAssessmentModelBean);

        TaxDeclarationModelBean model = setupModel();
        model.getTaxDeclarationOverviews().get(0).setAssessedTotal(BigDecimal.valueOf(-1));
        model.setCompletionOfProcessingModel(completionOfProcessingGeneralPanelModelBean);
        injectModel(model);

        when(this.ds141TaxDeclarationServiceLocalFacade.fetchAllRiskAssessments(any())).thenReturn(
                new ArrayList<>(Arrays.asList(RISK1)));
        when(this.taxationFacade.compareLegalBasisLabels(anyString(), any())).thenReturn(Boolean.TRUE);

        // when
        this.sut.onPanelOpen();

        // then
        this.softly.assertThat(model.getCompletionOfProcessingModel().getOverviewTaxAssessmentModelBean()
                .getSelectionTaxReliefForShippingOrAviation().size()).isEqualTo(0);
    }


    /*
     * TestCase for
     * when SelectionTaxReliefForShippingOrAviation has some values;
     */
    @Test
    public void shouldHandlePanelOpenWhenSelectionTaxReliefForShippingOrAviationHasValues() throws MoeveBusinessException
    {
        // given
        Af202CompletionOfProcessingGeneralPanelModelBean completionOfProcessingGeneralPanelModelBean =
                new Af202CompletionOfProcessingGeneralPanelModelBean();

        OverviewTaxAssessmentModelBean overviewTaxAssessmentModelBean = new OverviewTaxAssessmentModelBean();
        overviewTaxAssessmentModelBean.getSelectionTaxReliefForShippingOrAviation().add("abc");
        overviewTaxAssessmentModelBean.getSelectionTaxReliefForShippingOrAviation().add("lmn");
        overviewTaxAssessmentModelBean.getSelectionTaxReliefForShippingOrAviation().add("xyz");

        completionOfProcessingGeneralPanelModelBean.setOverviewTaxAssessmentModelBean(
                overviewTaxAssessmentModelBean);

        TaxDeclarationModelBean model = setupModel();
        model.getTaxDeclarationOverviews().get(0).setAssessedTotal(BigDecimal.valueOf(-1));
        model.setCompletionOfProcessingModel(completionOfProcessingGeneralPanelModelBean);
        injectModel(model);

        when(this.ds141TaxDeclarationServiceLocalFacade.fetchAllRiskAssessments(any())).thenReturn(
                new ArrayList<>(Arrays.asList(RISK1)));
        when(this.taxationFacade.compareLegalBasisLabels(anyString(), any())).thenReturn(Boolean.TRUE);

        // when
        this.sut.onPanelOpen();

        // then
        this.softly.assertThat(model.getCompletionOfProcessingModel().getOverviewTaxAssessmentModelBean()
                .getSelectionTaxReliefForShippingOrAviation().size()).isEqualTo(0);
    }


    @Test
    public void shouldInitializeRiskAssessmentDataWhenRiskSetIsNotEmpty()
    {
        // given
        TaxDeclarationModelBean model = setupModel(Set.of(RISK1));

        when(this.ds141TaxDeclarationServiceLocalFacade.fetchAllRiskAssessments(any())).thenReturn(
                new ArrayList<>(Arrays.asList(RISK2)));

        // when
        this.sut.initializeRiskAssessmentData(model);

        // then
        this.softly.assertThat(model.getAllRiskAssessment()).containsExactlyInAnyOrder(RISK1, RISK2);

    }


    @Test
    public void shouldInitializeRiskAssessmentDataWhenRiskSetIsEmpty()
    {
        // given
        TaxDeclarationModelBean model = setupModel(new HashSet<>());

        when(this.ds141TaxDeclarationServiceLocalFacade.fetchAllRiskAssessments(any())).thenReturn(
                Stream.of(RISK1, RISK2).collect(Collectors.toList()));

        // when
        this.sut.initializeRiskAssessmentData(model);

        // then
        this.softly.assertThat(model.getAllRiskAssessment()).containsExactlyInAnyOrder(RISK1, RISK2);
    }


    @Test
    public void shouldHandleDuplicateRisksWhenFetchedRisksContainDuplicates()
    {
        // given
        TaxDeclarationModelBean model = setupModel(Set.of(RISK1, UNIQUE_RISK));

        when(this.ds141TaxDeclarationServiceLocalFacade.fetchAllRiskAssessments(any())).thenReturn(
                Stream.of(RISK1, RISK2).collect(Collectors.toList()));

        // when
        this.sut.initializeRiskAssessmentData(model);

        // then
        this.softly.assertThat(model.getAllRiskAssessment()).containsExactlyInAnyOrder(RISK1, RISK2, UNIQUE_RISK);
    }


    @Test
    public void shouldHandleEmptyFetchedRisksWhenNoRisksAreFetched()
    {
        // given
        TaxDeclarationModelBean model = setupModel(Set.of(RISK1));

        when(this.ds141TaxDeclarationServiceLocalFacade.fetchAllRiskAssessments(any())).thenReturn(
                new ArrayList<String>());

        // when
        this.sut.initializeRiskAssessmentData(model);

        // then
        this.softly.assertThat(model.getAllRiskAssessment()).containsExactlyInAnyOrder(RISK1);
    }


    @Test
    public void shouldClearRiskAssessmentWhenRiskChangedToFalse()
    {
        // given
        TaxDeclarationModelBean model = setupModel(RISK_DISABLED);
        injectModel(model);

        // when
        this.sut.riskOnChange();

        // then
        this.softly.assertThat(model.getRiskAssessment()).isEmpty();
        this.softly.assertThat(model.getCompletionOfProcessingModel().isRiskAssessmentCheckboxEnabled()).isFalse();
        this.softly.assertThat(model.getCompletionOfProcessingModel().isRiskAssessmentCheckboxRequired()).isFalse();
    }


    @Test
    public void shouldPopulateRiskAssessmentWhenRiskChangedToTrue()
    {
        // given
        TaxDeclarationModelBean model = setupModel(RISK_ENABLED);
        confgureViewMode(ScreenOperationModeDt.STANDARD);

        injectModel(model);

        // when
        this.sut.riskOnChange();

        // then
        this.softly.assertThat(model.getRiskAssessment()).isNotEmpty();
        this.softly.assertThat(model.getCompletionOfProcessingModel().isRiskAssessmentCheckboxEnabled()).isTrue();
        this.softly.assertThat(model.getCompletionOfProcessingModel().isRiskAssessmentCheckboxRequired()).isTrue();
    }


    @Test
    public void shouldEnableAndRequireRiskAssessmentCheckboxWhenRiskIsTrueAndModeIsStandard()
    {
        // given
        TaxDeclarationModelBean model = setupModel(RISK_ENABLED);
        confgureViewMode(ScreenOperationModeDt.STANDARD);

        // when
        this.sut.configureRiskAssessmentCheckbox(model);

        // then
        Af202CompletionOfProcessingGeneralPanelModelBean componentModel = model.getCompletionOfProcessingModel();
        this.softly.assertThat(componentModel.isRiskAssessmentCheckboxEnabled()).isTrue();
        this.softly.assertThat(componentModel.isRiskAssessmentCheckboxRequired()).isTrue();
    }


    @Test
    public void shouldDisableRiskAssessmentCheckboxWhenRiskIsTrueAndModeIsNotStandard()
    {
        // given
        TaxDeclarationModelBean model = setupModel(RISK_ENABLED);

        confgureViewMode(ScreenOperationModeDt.HISTORIZATION);

        // when
        this.sut.configureRiskAssessmentCheckbox(model);

        // then
        Af202CompletionOfProcessingGeneralPanelModelBean componentModel = model.getCompletionOfProcessingModel();
        this.softly.assertThat(componentModel.isRiskAssessmentCheckboxEnabled()).isFalse();
        this.softly.assertThat(componentModel.isRiskAssessmentCheckboxRequired()).isFalse();
    }


    @Test
    public void shouldDisableRiskAssessmentCheckboxWhenRiskIsFalseAndModeIsStandard()
    {
        // given
        TaxDeclarationModelBean model = setupModel(RISK_DISABLED);

        // when
        this.sut.configureRiskAssessmentCheckbox(model);

        // then
        Af202CompletionOfProcessingGeneralPanelModelBean componentModel = model.getCompletionOfProcessingModel();
        this.softly.assertThat(componentModel.isRiskAssessmentCheckboxEnabled()).isFalse();
        this.softly.assertThat(componentModel.isRiskAssessmentCheckboxRequired()).isFalse();
    }


    @Test
    public void shouldDisableRiskAssessmentCheckboxWhenRiskIsFalseAndModeIsNotStandard()
    {
        // given
        TaxDeclarationModelBean model = setupModel(RISK_DISABLED);

        // when
        this.sut.configureRiskAssessmentCheckbox(model);

        // then
        Af202CompletionOfProcessingGeneralPanelModelBean componentModel = model.getCompletionOfProcessingModel();
        this.softly.assertThat(componentModel.isRiskAssessmentCheckboxEnabled()).isFalse();
        this.softly.assertThat(componentModel.isRiskAssessmentCheckboxRequired()).isFalse();
    }


    @Test
    public void shouldSetSelectionShippingAviationToTrueWhenLegalBasisMatchesAndTotalNotAssessed()
            throws MoeveBusinessException
    {
        // given
        TaxDeclarationModelBean model = setupModelWithOverview(false, false);

        when(this.taxationFacade.compareLegalBasisLabels(any(), any())).thenReturn(true);

        // when
        this.sut.hideSelectionTaxReliefForShippingOrAviation(model);

        // then
        this.softly.assertThat(model.getCompletionOfProcessingModel().getOverviewTaxAssessmentModelBean()
                .getIsSelectionShippingAviation()).isTrue();
    }


    @Test
    public void shouldNotChangeSelectionShippingAviationWhenLegalBasisDoesNotMatch() throws MoeveBusinessException
    {
        // given
        TaxDeclarationModelBean model = setupModelWithOverview(true, false);

        when(this.taxationFacade.compareLegalBasisLabels(any(), any())).thenReturn(false);

        // when
        this.sut.hideSelectionTaxReliefForShippingOrAviation(model);

        // then
        this.softly.assertThat(model.getCompletionOfProcessingModel().getOverviewTaxAssessmentModelBean()
                .getIsSelectionShippingAviation()).isFalse();
    }


    @Test
    public void shouldClearSelectionShippingAviationWhenLegalBasisMatchesAndTotalIsAssessed()
            throws MoeveBusinessException
    {
        // given
        TaxDeclarationModelBean model = setupModelWithOverview(true, true);

        when(this.taxationFacade.compareLegalBasisLabels(any(), any())).thenReturn(true);

        // when
        this.sut.hideSelectionTaxReliefForShippingOrAviation(model);

        // then
        this.softly.assertThat(model.getCompletionOfProcessingModel().getOverviewTaxAssessmentModelBean()
                .getIsSelectionShippingAviation()).isFalse();
        this.softly.assertThat(model.getCompletionOfProcessingModel().getOverviewTaxAssessmentModelBean()
                .getSelectionTaxReliefForShippingOrAviation()).isEmpty();
    }


    private TaxDeclarationModelBean setupModel()
    {
        TaxDeclarationModelBean model = TestDataHelper.fillAllEmptyFields(new TaxDeclarationModelBean());
        model.setCompletionOfProcessingModel(new Af202CompletionOfProcessingGeneralPanelModelBean());
        model.setIsAf202Enabled(RISK_ENABLED);
        model.getBasicData().setCaseType(CaseTypeDt.TAX_DECLARATION_1100);

        return model;

    }


    private TaxDeclarationModelBean setupModel(final Set<String> risksSet)
    {
        TaxDeclarationModelBean model = setupModel();
        model.setRiskAssessment(risksSet);

        return model;
    }


    private TaxDeclarationModelBean setupModel(final boolean risk)
    {
        TaxDeclarationModelBean model = setupModel();
        model.setRisk(risk);

        return model;
    }


    private TaxDeclarationModelBean setupModelWithOverview(final boolean assessed,
            final boolean initialIsSelectionShippingAviation)
    {
        TaxDeclarationModelBean model = setupModel();

        List<TaxDeclarationOverviewModelBean> overviews = new ArrayList<>();
        TaxDeclarationOverviewModelBean overviewModel = new TaxDeclarationOverviewModelBean();
        overviewModel.setLegalBasisId(24L);
        overviewModel.setLegalBasisAdditionID(56L);

        BigDecimal assessedTotal = assessed ? BigDecimal.ZERO : BigDecimal.valueOf(1);
        overviewModel.setAssessedTotal(assessedTotal);

        overviews.add(overviewModel);
        model.setTaxDeclarationOverviews(overviews);

        OverviewTaxAssessmentModelBean assessmentModel = new OverviewTaxAssessmentModelBean();
        assessmentModel.setIsSelectionShippingAviation(initialIsSelectionShippingAviation);

        model.getCompletionOfProcessingModel().setOverviewTaxAssessmentModelBean(assessmentModel);

        return model;
    }


    private void confgureViewMode(final ScreenOperationModeDt screenMode)
    {
        when(this.tabViewParamModelBean.getMode()).thenReturn(screenMode);
    }

}
